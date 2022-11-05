import re
from urllib.parse import *
from bs4 import BeautifulSoup
from auxiliary import *
import nltk
import statistics


"""
Quoted works:
    For the simhash dependency: https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
    
    Quoted the types of crawler traps: 
        1. Author: jamessykwan (James Kwan) URL: https://github.com/jamessykwan/cs121-webcrawler
        2. https://www.contentkingapp.com/academy/crawler-traps/
    
    Inspired by this work about how to collect the statistics and generate the report 
    using a class instead of what I used to do: a json file. Python class has different kinds of 
    data structures to store data which json lacks: https://github.com/jamessykwan/cs121-webcrawler
    
"""


def scraper(url, resp, statistics):

    if resp.status == 200 and is_valid(resp.url):

        statistics.unique_pages += 1
        if ".ics.uci.edu" in url:
            if "www." in url:
                subdomain = url[url.index(
                    "www.") + 4: url.index("ics.uci.edu")] + "ics.uci.edu"
            else:
                subdomain = url[url.index(
                    "//") + 2: url.index("ics.uci.edu")] + "ics.uci.edu"
            if subdomain in statistics.ics_uci_edu_subdomains.keys():
                statistics.ics_uci_edu_subdomains[subdomain] += 1
            else:
                statistics.ics_uci_edu_subdomains[subdomain] = 1

        word_tokens = filter_words(resp)
        frequency_map = nltk.FreqDist(word_tokens)
        sorted_freqs = sorted(frequency_map.items(),
                              key=lambda x: x[1], reverse=True)
        for word, freq in sorted_freqs:
            if word not in statistics.word_frequency_map:
                statistics.word_frequency_map[word] = freq
            else:
                statistics.word_frequency_map[word] += freq

        words = [k for k, v in sorted_freqs]
        freqs = [v for k, v in sorted_freqs]
        total_weight = sum(freqs)

        # avoid large pages with low information to be the longest page
        if total_weight > statistics.most_weight:
            statistics.most_weight = total_weight
            statistics.longest_page_val = len(words)
            statistics.longest_page = url

        next_links = extract_next_links(url, resp)

        return next_links

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
        scraped_link = link['href']
        if scraped_link.startswith('/') and not scraped_link.startswith('//'):
            if 'today.uci.edu/department/information_computer_sciences' in url:
                domain = url[:url.index(
                    "today.uci.edu/department/information_computer_sciences") + 54]
                scraped_link = domain + scraped_link
            else:
                domain = url[:url.index(".uci.edu") + 8]
                scraped_link = domain + scraped_link
        if "#" in scraped_link:
            scraped_link = scraped_link[:scraped_link.index("#")]
        if is_valid(scraped_link) and scraped_link not in next_links:
            next_links.append(scraped_link)

    return next_links


def filter_words(resp):
    # avoid pages with no data
    if not resp.raw_response.content:
        return []

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    input_text = soup.get_text()

    if len(input_text) < 200:
        return []

    word_tokens = tokenize(input_text)
    stop_words = STOP_WORDS
    word_tokens_without_stopwords = [
        token.lower() for token in word_tokens if token.lower() not in stop_words and token.isalpha()]
    return word_tokens_without_stopwords


def tokenize(input_text):
    token_list = []
    pattern = '^[a-zA-Z0-9\']+$'  # include the single quotation mark
    for word in input_text.split():
        if re.match(pattern, word):
            token_list.append(word)
    return token_list


def is_seed_url(parsed):
    for domain in SEED_URLS:
        if domain in parsed.netloc or (
                'today.uci.edu' in parsed.netloc and '/department/information_computer_sciences' == parsed.path[
                    :len(
                        '/department/information_computer_sciences')]):
            return True
    return False


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if not is_seed_url(parsed):
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
    # is infinite loop:
    parsed = urlparse(url)
    path = parsed.path  # avoid the repeating url loop
    parts = path.split("/")
    part_set = set()
    for part in parts:
        if part not in part_set:
            part_set.add(part)
        else:
            return True

    # is calender: dynamically generated content
    if re.match(r"^.*calendar.*$", path.lower()):
        return True

    trap_list = ["txt", ".pdf", "?share=twitter", "?share=facebook",
                 "?action=login", ".zip", ".java", ".xml", ".bib", "tar.gz", ".htm"]
    for trap_element in trap_list:
        if url.endswith(trap_element):
            return True

    if "doku.php" in url and "?" in url:
        return True

    if "grape.ics.uci.edu" in url and ("action=diff&version=" in url or "timeline?from" in url or ("?version=" in url and not url.endswith("?version=1"))):
        return True

    return False
