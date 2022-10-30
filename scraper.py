import json
import re
from urllib.parse import *
from bs4 import BeautifulSoup
import requests
from auxiliary import *


# Quoted works:
#    For the help of building the scraper:
#        Author: Eric Sangyun Ko (https://github.com/Thundelly), Natcha Jengjirapas (https://github.com/rew35860)
#        URL: https://github.com/Thundelly/CS121-Web-Crawler
# Used nltk library to tokenize text content and import the English stop words

def scraper(url, resp):
    scraped_links = extract_next_links(url, resp)
    filtered_links = filter_urls(scraped_links)

    if resp.status == 200:
        get_link_dict(filtered_links)
        filter_words(url, resp)

    return filtered_links


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

    try:
        if resp.status == 200:
            parsed = urlparse(url)
            cur_host = parsed.scheme + parsed.netloc

            soup = BeautifulSoup(resp.raw_response, 'html.parser')
            for link in soup.findAll('a', href=True):
                try:
                    whole_url = urljoin(cur_host, link['href'])
                    pure_url, fragment = urldefrag(whole_url)
                    next_links.append(pure_url)

                except KeyError:
                    print(f"Status Code: {resp.status} \n Error Message: Missing href attribute in the anchor tag!")

        else:
            print(f"Status Code {resp.status} is not 200 \n Error Message: {resp.error}")

    except AttributeError:
        print(f"Status Code {resp.status} \n Error Message: {resp.error}")

    return next_links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        is_valid_url = False
        for domain in SEED_URLS:
            if domain in parsed.netloc or (
                    'today.uci.edu' in parsed.netloc and '/department/information_computer_sciences' == parsed.path[
                                                                                                        :len(
                                                                                                            '/department/information_computer_sciences')]):
                is_valid_url = True

        if not is_valid_url:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def filter_urls(urls):
    valid_links = []
    for url in urls:
        if is_valid(url):
            valid_url = url

            parsed_url = urlparse(url)
            if parsed_url.path == '':
                valid_url += '/'
            valid_links.append(valid_url)

    return valid_links


def tokenize(input_text):
    token_list = []
    pattern = '^[a-zA-Z0-9\']+$'  # include the single quotation mark
    for word in input_text.split():
        if re.match(pattern, word):
            token_list.append(word)
    return token_list


def get_link_dict(filtered_links):
    try:
        with open('link_dict.json', 'r') as link_json_file:
            link_dict = json.load(link_json_file)
    except json.decoder.JSONDecodeError:
        link_dict = {
            'counter': {
                'total_number_of_pages': 0,
                'ics.uci.edu_subdomains': {}
            }
        }

    for link in filtered_links:
        parsed = urlparse(link)
        subdomain, domain = parsed.netloc.split('.', 1)
        path = parsed.path

        if_find_subdomain = False
        if domain not in link_dict:
            link_dict[domain] = [{subdomain: [path]}]
            link_dict['counter']['total_number_of_pages'] += 1
            if domain == 'ics.uci.edu':
                link_dict['counter']['ics.uci.edu_subdomains'][subdomain] = 1
        else:
            for included_subdomains in link_dict['domain']:
                if subdomain in included_subdomains:
                    if path not in included_subdomains[subdomain]:
                        included_subdomains[subdomain].append(path)
                        link_dict['counter']['total_number_of_pages'] += 1
                        if domain == 'ics.uni.edu':
                            link_dict['counter']['ics.uci.edu_subdomains'][subdomain] += 1

    with open('link_dict.json', 'w') as link_json_file:
        json.dump(link_dict, link_json_file)


def filter_words(url, resp):
    try:
        with open('word_dict.json', 'r') as word_json_file:
            word_dict = json.load(word_json_file)
    except json.decoder.JSONDecodeError:
        word_dict = {
            'url_list': {},
            'word_list': {},
            'counter': {
                'url_with_most_words': {},
                '50_most_frequent_words': {}
            }
        }

    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        input_text = soup.text
        word_tokens = tokenize(input_text)
        stop_words = STOP_WORDS
        word_tokens_without_stopwords = [token for token in word_tokens if token not in stop_words]

        word_dict['url_list'][url] = len(word_tokens)

        try:
            cur_number_of_words = list(word_dict['counter']['url_with_most_words'].values())[0]
            if len(word_tokens) > cur_number_of_words:
                word_dict['counter']['url_with_most_words'] = {}
                word_dict['counter']['url_with_most_words'][url] = len(word_tokens)

        except IndexError:
            word_dict['counter']['url_with_most_words'][url] = len(word_tokens)

        for token in word_tokens_without_stopwords:
            if token not in word_dict['word_list']:
                word_dict['word_list'][token] = 1
            else:
                word_dict['word_list'][token] += 1

        with open('word_dict.json', 'w') as word_json_file:
            json.dump(word_dict, word_json_file)

    except AttributeError:
        print(f"Status Code: {resp.status} \n Error Message: {resp.error}")
