import re
from urllib.parse import *
from bs4 import BeautifulSoup
from auxiliary import *
from simhash import Simhash
import link_stat, word_stat
import time

"""
Quoted works:
    For the simhash dependency: https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
"""


def if_near_duplicate(current_page, simhash_list):
    for simhash_value in simhash_list:
        distance = Simhash(current_page).distance(simhash_value)
        if distance <= HAMMING_DISTANCE:
            return True
    return False
    
    
def scraper(url, resp):

    if resp.status == 200:
        word_tokens = filter_words(resp)
        content = ' '.join(word_tokens)
        
        # avoid pages with low information
        if len(content) < 200:
            return []
        
        # avoid near duplicate pages
        if if_near_duplicate(content, SIMHASH_LIST_30_PAGES):
            return [];
        else:
            SIMHASH_LIST_30_PAGES.append(Simhash(content))
            if len(SIMHASH_LIST_30_PAGES > 30):
                SIMHASH_LIST_30_PAGES.pop(0)
        
        link_stat.unique_links.add(url)
        
        next_links = extract_next_links(url, resp)
        
        if len(word_tokens) > list(word_stat.page_with_most_words.values())[0]:
            word_stat.page_with_most_words = {}
            word_stat.page_with_most_words[url] = len(word_tokens)
        
        for token in word_tokens:
            token = token.lower()
            if token in word_stat.word_frequency_map.keys():
                word_stat.word_frequency_map[token] += 1
            else:
                word_stat.word_frequency_map[token] = 1

        parsed = urlparse(url)
        if ('.ics.uci.edu' in parsed.hostname):
            if parsed.hostname in link_stat.ics_uci_edu_subdomains.keys():
                link_stat.ics_uci_edu_subdomains[parsed.hostname].add(url)
            else:
                link_stat.ics_uci_edu_subdomains[parsed.hostname] = set()

        return [link for link in next_links if is_valid(link)]

    else:
        return []


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    next_links = []
    if not resp.raw_response:
        return next_links
    
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for link in soup.findAll('a', href=True):
        scraped_link = link.get('href')
        pure_url, fragment = urldefrag(scraped_link)
        if (str(pure_url).startswith('/')):
            pure_url = url + str(pure_url)
        if is_valid(pure_url):
            next_links.append(pure_url)
            
    return next_links
       

def filter_words(resp):
    # avoid pages with no data
    if not resp.raw_response.content:
        return [];
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    input_text = soup.text
    word_tokens = tokenize(input_text)
    stop_words = STOP_WORDS
    word_tokens_without_stopwords = [
        token for token in word_tokens if token not in stop_words]
    return word_tokens_without_stopwords


def tokenize(input_text):
    token_list = []
    pattern = '^[a-zA-Z0-9\']+$'  # include the single quotation mark
    for word in input_text.split():
        if re.match(pattern, word):
            token_list.append(word)
    return token_list


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        is_seed_url = False
        for domain in SEED_URLS:
            if domain in parsed.netloc or (
                    'today.uci.edu' in parsed.netloc and '/department/information_computer_sciences' == parsed.path[
                        :len(
                            '/department/information_computer_sciences')]):
                is_seed_url = True

        if not is_seed_url:
            return False

        if is_spider_trap(url):
            return False
        
        return not re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                    + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower())
        
    except TypeError:
        print("TypeError for ", parsed)
        raise



def is_spider_trap(url):
    path = urlparse(url).path
    parts = path.split("/")
    part_set = set()
    for part in parts:
        if part not in part_set:
            part_set.add(part)
        else:
            return True
    


    







