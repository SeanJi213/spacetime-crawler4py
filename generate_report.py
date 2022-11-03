import link_stat, word_stat


def get_most_frequent_50_words():
    sorted_word_dict = sorted(word_stat.word_frequency_map.items(), key=lambda x: x[1], reverse=True)
    most_frequent_50 = []
    if (len(sorted_word_dict) <= 50):
        for word, frequency in sorted_word_dict:
            most_frequent_50.append([word, frequency])
    else:
        words = list(sorted_word_dict.keys())[:50]
        frequencies = list(sorted_word_dict.values())[:50]
        for i in range(50):
            most_frequent_50.append([words[i], frequencies[i]])
    return most_frequent_50


with open('report.txt', 'w') as report_file:
    number_unique_links = len(link_stat.unique_links)
    report_file.write(f'The number of unique pages is {number_unique_links}\n\n')
    report_file.write(f'Page with most words: {list(word_stat.page_with_most_words.keys())[0]} \t Number of words: {list(word_stat.page_with_most_words.values())[0]}\n\n')
    report_file.write('50 most frequent words: \n')
    frequent_words = get_most_frequent_50_words()
    for el in frequent_words:
        report_file.write(f'\t{el[0]}: {el[1]}\n')
    
    report_file.write('\n')
    report_file.write('ics.uci.edu subdomains and their corresponding number of pages:\n')
    
    for subdomain, pages in sorted(link_stat.ics_uci_edu_subdomains.items(), key=lambda item: item[0].lower()):
        report_file.write(f'\t{subdomain}: {len(pages)}\n')
    
    report_file.close()
    

