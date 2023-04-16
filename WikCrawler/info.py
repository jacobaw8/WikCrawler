#!/usr/bin/env python3
import requests
import sys
import os
import re
from bs4 import BeautifulSoup
from bs4 import Comment
import concurrent.futures
import random
from requests.api import get

try:
    width,height = os.get_terminal_size()
    p = True
except OSError:
    width = 120
    height = 80
    p = False

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
colors = ['\033[92m','\033[95m','\033[96m','\033[94m','\033[36m']

q_flag = 0

# Makes request to wikipedia for the code
def req(term,lang="en"):
    global wikiurl 
    wikiurl = "https://"+lang+".wikipedia.org/wiki/"+term
    r = requests.get(wikiurl)
    return r.text

#  Gets summary
def getSummary(term,lang="en"):
    final_content = []
    content = req(term,lang)
    soup = BeautifulSoup(content,'html.parser')
    content = soup.find_all('p')
    n_links = []
    print('\n'+(color.BOLD+str(term)).center(width,"-")+ "\n"+color.END) 
    for i in content:
        if i.get_text() == "\n": continue
        else:
            if i('sup'):
                for tag in i('sup'): tag.decompose() 
            data = i.get_text()
            final_content.append(data)
            if len(final_content) == 3: break 
    if "may refer to:" in str(i):
        print("Did You Mean: ")
        term = searchInfo(term)
    else:
        print(color.BLUE) 
        print(*final_content,sep = '\n\n')
        print(color.END)
        for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
            n_links.append(link.get('href'))
        print('\n'+(color.BOLD+'Credible References Used').center(width,"-")+ "\n"+color.END)
        print(n_links)
        print("\n")
    with open('OUTPUT.txt', 'w') as f:
        for j in final_content:
            f.write(str(j) + "\n")
        for n in n_links:
            f.write(str(n)+ "\n")



def getInfo(term,lang="en"):
    f = open('OUTPUT.txt', 'w')

    final_content = []
    content = req(term,lang)
    soup = BeautifulSoup(content,'html.parser')
    content = []
    for a in soup.find_all(['p','span']):
        try:
            if a['class'] and 'mw-headline' in a['class']:
                content.append(a)
        except KeyError:
            if a.name == 'p':
                content.append(a)
    for i in content:
        if i('sup'):
            for tag in i('sup'): 
                tag.decompose()   
        data = i.get_text()
        if i.name == 'span': 
            final_content.append('!'+str(data))
        else: final_content.append(data)
    if "may refer to:" in str(final_content[0]): term = searchInfo(term)
    else:
        if p == True: 
            print('\n'+(color.BOLD+str(term)).center(width,"-")+color.END+'\n')
            print(str(wikiurl).center(width," ")+color.END+'\n')
            f.write('\n'+(color.BOLD+str(term)).center(width,"-")+color.END+'\n')
            f.write(str(wikiurl).center(width," ")+color.END+'\n')
        else:
            print('\n'+str(term).center(width,"-"))
            print('\n'+str(wikiurl).center(width, " ")+'\n')
            f.write('\n'+str(term).center(width,"-"))
            f.write('\n'+str(wikiurl).center(width, " ")+'\n')
        for i in final_content:
            if i == "\n": continue
            if i in ["!See also","!Notes","!References","!External links","!Further reading"]: continue
            else:
                if p == True:
                    if str(i[0]) == '!':
                         print(color.BOLD+i[1:]+color.END+color.END)
                         print("-"*(len(i)+1))
                         f.write(color.BOLD+i[1:]+color.END+color.END)
                         f.write("-"*(len(i)+1))
                    else:   
                        if "Other reasons this message may be displayed:" in i:searchInfo(term)
                        else:
                            print(color.BLUE+i+"\n"+color.END)
                            f.write(color.BLUE+i+"\n"+color.END)
                else: 
                    print(str(i)+'\n')
                    f.write(str(i)+'\n')


# Search for Similar Articles
def searchInfo(term,lang="en"):
    f = open('OUTPUT.txt', 'w')
    final_content = []
    r = requests.get("https://"+lang+".wikipedia.org/w/index.php?search="+term)
    if '/wiki/' in r.url:
        q_flag = 1
        getInfo(term)
    else:
        content = r.text
        soup = BeautifulSoup(content,'html.parser')
        content = soup.find_all('a')
        did = soup.find('a',{'id':'mw-search-DYM-suggestion'})
        for i in content:
            if i.get('title') == i.get_text():
                final_content.append(i.get_text())
        final_content = final_content[2:]
        print("Did You Mean: \n")
        f.write("Did You Mean: \n")
        if did is not None:
            print(did.get_text())
            print(*final_content[:5],sep ="\n")
            f.write(did.get_text())
            f.write(*final_content[:5],sep ="\n")
        else:
            print(*final_content[:5],sep="\n")
            f.write(*final_content[:5],sep="\n")





def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    grab = BeautifulSoup(body, 'html.parser')
    texts = grab.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def search_links(link, query):
    #print(link)
    try:
        new_page = requests.get(link['href'], timeout=5)

        if(new_page):
            page_text = text_from_html(new_page.text)
            count = page_text.count(query)
            if(count >= 1):
                print(str(count) + "\t\t " + link['href'])
                file = open('OUTPUT.txt', 'a')
                file.write(str(count) + "\t\t " + link['href'] + "\n")
                return count
    except:
        return

def start_search(grab, query):
    executor = concurrent.futures.ThreadPoolExecutor(20)
    futures = [executor.submit(search_links, link, query) for link in grab.findAll('a', attrs={'href': re.compile("^http://")})]
    concurrent.futures.wait(futures)






# Gets summary
def getSummaryOccurences(term, query, lang="en"):
    f = open('OUTPUT.txt', 'w')
    final_content = []
    content = req(term,lang)
    soup = BeautifulSoup(content,'html.parser')

    content = soup.find_all('p')
    n_links = []
    print('\n'+(color.BOLD+str(term)).center(width,"-")+ "\n"+color.END) 
    for i in content:
        if i.get_text() == "\n": continue
        else:
            if i('sup'):
                for tag in i('sup'): tag.decompose() 
            data = i.get_text()
            final_content.append(data)
            if len(final_content) == 3: break 
    if "may refer to:" in str(i):
        print("Did You Mean: ")
        term = searchInfo(term)
    else:
        print(color.BLUE) 
        print(*final_content,sep = '\n\n')
        print(color.END)
        for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
            n_links.append(link.get('href'))
        print('\n'+(color.BOLD+'Credible References Used').center(width,"-")+ "\n"+color.END)
        print(n_links)
        print("\n")
    for j in final_content:
        f.write(str(j) + "\n")
    for n in n_links:
        f.write(str(n)+ "\n")
    print("Your query appears in the following references: ")
    print("==================================================================")
    print("Occurences\t Link")
    f.write("Your query appears in the following references: \n")
    f.write("==================================================================\n")
    f.write("Occurences\t Link\n")
    f.close()
    start_search(soup,query)


def getInfoOccurences(term, query, lang="en"):
    f = open('OUTPUT.txt', 'w')

    final_content = []
    content = req(term,lang)
    soup = BeautifulSoup(content,'html.parser')
    content = []
    for a in soup.find_all(['p','span']):
        try:
            if a['class'] and 'mw-headline' in a['class']:
                content.append(a)
        except KeyError:
            if a.name == 'p':
                content.append(a)
    for i in content:
        if i('sup'):
            for tag in i('sup'): 
                tag.decompose()   
        data = i.get_text()
        if i.name == 'span': 
            final_content.append('!'+str(data))
        else: final_content.append(data)
    if "may refer to:" in str(final_content[0]): term = searchInfo(term)
    else:
        if p == True: 
            print('\n'+(color.BOLD+str(term)).center(width,"-")+color.END+'\n')
            print(str(wikiurl).center(width," ")+color.END+'\n')
            f.write('\n'+(color.BOLD+str(term)).center(width,"-")+color.END+'\n')
            f.write(str(wikiurl).center(width," ")+color.END+'\n')
        else:
            print('\n'+str(term).center(width,"-"))
            print('\n'+str(wikiurl).center(width, " ")+'\n')
            f.write('\n'+str(term).center(width,"-"))
            f.write('\n'+str(wikiurl).center(width, " ")+'\n')
        for i in final_content:
            if i == "\n": continue
            if i in ["!See also","!Notes","!References","!External links","!Further reading"]: continue
            else:
                if p == True:
                    if str(i[0]) == '!':
                         print(color.BOLD+i[1:]+color.END+color.END)
                         print("-"*(len(i)+1))
                         f.write(color.BOLD+i[1:]+color.END+color.END)
                         f.write("-"*(len(i)+1))
                    else:   
                        if "Other reasons this message may be displayed:" in i:searchInfo(term)
                        else:
                            print(color.BLUE+i+"\n"+color.END)
                            f.write(color.BLUE+i+"\n"+color.END)
                else: 
                    print(str(i)+'\n')
                    f.write(str(i)+'\n')

    print("Your query appears in the following references: ")
    print("==================================================================")
    print("Occurences\t Link")
    f.write("Your query appears in the following references: \n")
    f.write("==================================================================\n")
    f.write("Occurences\t Link\n")
    start_search(soup,query)
    f.close()


# Search for Similar Articles
def searchInfoOccurences(term, query, lang="en"):
    f = open('OUTPUT.txt', 'w')
    final_content = []
    r = requests.get("https://"+lang+".wikipedia.org/w/index.php?search="+term)
    if '/wiki/' in r.url:
        q_flag = 1
        getInfo(term)
        soup = BeautifulSoup(r.text,'html.parser')
        print("Your query appears in the following references: ")
        print("==================================================================")
        print("Occurences\t Link")
        f.write("Your query appears in the following references: \n")
        f.write("==================================================================\n")
        f.write("Occurences\t Link\n")
        start_search(soup,query)
        f.close()    
    else:
        content = r.text
        soup = BeautifulSoup(content,'html.parser')
        content = soup.find_all('a')
        did = soup.find('a',{'id':'mw-search-DYM-suggestion'})
        for i in content:
            if i.get('title') == i.get_text():
                final_content.append(i.get_text())
        final_content = final_content[2:]
        print("Did You Mean: \n")
        f.write("Did You Mean: \n")
        if did is not None:
            print(did.get_text())
            print(*final_content[:5],sep ="\n")
            f.write(did.get_text())
            f.write(*final_content[:5],sep ="\n")
        else:
            print(*final_content[:5],sep="\n")
            f.write(*final_content[:5],sep="\n")

        print("Your query appears in the following references: ")
        print("==================================================================")
        print("Occurences\t Link")
        f.write("Your query appears in the following references: \n")
        f.write("==================================================================\n")
        f.write("Occurences\t Link\n")
        start_search(soup,query)
        f.close()    
    
    

    