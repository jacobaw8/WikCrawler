#All imports
import time
import requests
import concurrent.futures

from requests import Session
from bs4 import BeautifulSoup as soup
from bs4 import Comment
import re

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    grab = soup(body, 'html.parser')
    texts = grab.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def find_links_on_page(page):
    grab2 = soup(page.text, "html.parser")
    total_count = 0
    for link in grab2.findAll('a', attrs={'href': re.compile("^http://")}):
        total_count += search_links(link, 2)
    return total_count
        

def search_links(link, depth):
    #print(link)
    
    try:
        new_page = requests.get(link['href'], timeout=5)
        if(depth == 1):
            count_for_all_external_links = find_links_on_page(new_page)
            #print(count_for_all_external_links)
        if(new_page):
            count = new_page.text.count(search)
            if(count >= 1):
                print(str(count) + "\t\t " + link['href'])
                return count
    except:
        return


def start_search(grab):
    executor = concurrent.futures.ThreadPoolExecutor(20)
    futures = [executor.submit(search_links, link, 1) for link in grab.findAll('a', attrs={'href': re.compile("^http://")})]
    concurrent.futures.wait(futures)

query = input("Enter a topic: ")

url = "https://en.wikipedia.org/wiki/" + query
headers = {'User-Agent':'Mozilla/5.0'}
page = requests.get(url)
grab = soup(page.text, "html.parser")

search = input("Success! What would you like to look up? ")
print("Occurences \t Link")

start_search(grab)