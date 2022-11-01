import json
import re
from urllib.parse import *
from bs4 import BeautifulSoup
from auxiliary import *
import time
from urllib.robotparser import RobotFileParser

"""
Quoted works:
   For the help of extracting the links from text contents:
       Author: Eric Sangyun Ko (https://github.com/Thundelly), Natcha Jengjirapas (https://github.com/rew35860)
       URL: https://github.com/Thundelly/CS121-Web-Crawler
"""


robot_txt = {}


def scraper(url, resp):

    scraped_links = extract_next_links(url, resp)
    filtered_links = []
    for url in scraped_links:
        if is_valid(scraped_links):
            filtered_links.append(url)

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
            cur_host = parsed.scheme + "://" + parsed.netloc

            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            for link in soup.findAll('a', href=True):
                try:
                    whole_url = urljoin(cur_host, link['href'])
                    # get rid of the fragment part
                    pure_url, fragment = urldefrag(whole_url)
                    # avoid the spider traps
                    path_temp = urlparse(pure_url).path.split("/")
                    el_set = set()
                    for el in path_temp:
                        if el not in el_set:
                            el_set.add(el)
                        else:
                            break
                        continue
                    pure_url = re.sub(
                        "(\?replytocom=.*|\?share=.*|\?n=https.*|\?1=.*|\?c=https.*|\?do=diff.*|\?rev=.*|\?action=login.*|\?action=edit.*|\?action=refcount.*|\?action=source.*|\?action=diff.*|\?action=download.*)", "", pure_url)
                    if pure_url not in next_links:
                        next_links.append(pure_url)
                except:
                    print(
                        f"Status Code: {resp.status} \n Error Message: href attribute does not exist.")

        else:
            print(
                f"Status Code {resp.status} is not 200 \n Error Message: {resp.error}")

    except:
        print(f"Status Code {resp.status} \n Error Message: {resp.error}")

    return next_links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    global robot_txt

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

        robot = robot_txt.get(parsed.netloc, None)
        if not robot:
            time.sleep(POLITENESS)
            robot = RobotFileParser(
                parsed.scheme + "://" + parsed.netloc + "/robots.txt")
            try:
                robot.read()
            except:
                pass
            robot_txt[parsed.netloc] = robot
        if robot.can_fetch("IR UF22 79766310", url):
            if re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                    + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
                return False
            if re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                    + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower()):
                return False

            return True
        # cannot fetch this url, return False
        return False
    except TypeError:
        print("TypeError for ", parsed)
        raise
    except:
        pass
    return False


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
    except:
        link_dict = {
            'counter': {
                'total_number_of_pages': 0,
                'ics.uci.edu_subdomains': {}
            }
        }

    for url in filtered_links:

        parsed = urlparse(url)
        subdomain, domain = parsed.netloc.split('.', 1)
        path = parsed.path

        if_find_subdomain = False

        if domain not in link_dict:
            link_dict[domain] = [{subdomain: [path]}]
            link_dict['counter']['total_number_of_pages'] += 1
            if domain == 'ics.uci.edu':
                link_dict['counter']['ics.uci.edu_subdomains'][subdomain] = 1
        else:
            for included_subdomains in link_dict[domain]:
                if subdomain in included_subdomains:
                    if_find_subdomain = True

            if not if_find_subdomain:
                link_dict[domain].append({subdomain: [path]})
                link_dict['counter']['total_number_of_pages'] += 1
                if domain == 'ics.uci.edu':
                    link_dict['counter']['ics.uci.edu_subdomains'][subdomain] = 1
            else:
                for sub in link_dict[domain]:
                    if subdomain == sub:
                        if path not in sub[subdomain]:
                            sub[subdomain].append(path)
                            link_dict['counter']['total_number_of_pages'] += 1
                            if domain == 'ics.uci.edu':
                                link_dict['counter']['ics.uci.edu_subdomains'][subdomain] += 1

    with open('link_dict.json', 'w') as link_json_file:
        json.dump(link_dict, link_json_file)


def filter_words(url, resp):
    try:
        with open('word_dict.json', 'r') as word_json_file:
            word_dict = json.load(word_json_file)
    except:
        word_dict = {
            'url_list': {},
            'word_list': {}
        }

    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        input_text = soup.text
        word_tokens = tokenize(input_text)
        stop_words = STOP_WORDS
        word_tokens_without_stopwords = [
            token for token in word_tokens if token not in stop_words]

        word_dict['url_list'][url] = len(word_tokens)

        for token in word_tokens_without_stopwords:
            if token not in word_dict['word_list']:
                if len(token) > 2 and token.endswith("s"):
                    token = token[:len(token) - 1]
                elif len(token) > 3 and token.endswith("es"):
                    token = token[:len(token) - 2]
                if token not in word_dict['word_list']:
                    word_dict['word_list'][token] = 1
                else:
                    word_dict['word_list'][token] += 1
            else:
                word_dict['word_list'][token] += 1

        # try:
        #     cur_number_of_words = list(word_dict['counter']['url_with_most_words'].values())[0]
        #     if len(word_tokens) > cur_number_of_words:
        #         word_dict['counter']['url_with_most_words'] = {}
        #         word_dict['counter']['url_with_most_words'][url] = len(word_tokens)

        # except IndexError:
        #     word_dict['counter']['url_with_most_words'][url] = len(word_tokens)

        # sorted_word_list = sorted(
        #     word_dict['word_list'].items(), key=lambda x: x[1], reverse=True)

        # if len(sorted_word_list) <= 50:
        #     most_frequent_50_words = list(sorted_word_list.keys())
        #     frequencies = list(sorted_word_list.values())
        #     for i in range(len(sorted_word_list)):
        #         word_dict['counter']['50_most_frequent_words'][
        #             most_frequent_50_words[i]] = frequencies[i]
        # else:
        #     most_frequent_50_words = list(sorted_word_list.keys())[:50]
        #     frequencies = list(sorted_word_list.values())[:50]
        #     for i in range(50):
        #         word_dict['counter']['50_most_frequent_words'].append(
        #             most_frequent_50_words[i], frequencies[i])

        with open('word_dict.json', 'w') as word_json_file:
            json.dump(word_dict, word_json_file)

    except AttributeError:
        print(f"Status Code: {resp.status} \n Error Message: {resp.error}")
