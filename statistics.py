class Statistics:
    def __init__(self):
        self.most_weight = 0
        self.longest_page = ""
        self.longest_page_val = 0
        self.unique_pages = 0
        self.word_frequency_map = {}
        self.ics_uci_edu_subdomains = {}
        
    
    def generate_report(self):
        with open('report.txt', 'w') as report_file:
            report_file.write(f'1. The number of unique pages is {self.unique_pages}\n\n')
            report_file.write(f'2. Longest page: {self.longest_page} \t Number of words: {self.longest_page_val}\n\n')
            
            sorted_freqs = sorted(self.word_frequency_map.items(), key=lambda x:x[1], reverse=True)
            report_file.write('3. 50 most common words: \n')
            most_frequent_50 = []
            for i in range(50):
                most_frequent_50.append(sorted_freqs[i])
            for i in range(50):
                report_file.write(f'{i + 1}. {most_frequent_50[i][0]}: {most_frequent_50[i][1]}\n')
            
            report_file.write('\n4. ics.uci.edu subdomains: \n')
            subdomains = [list(subdomain) for subdomain in self.ics_uci_edu_subdomains.items()]
            subdomains_alphabetically_sorted = sorted(subdomains, key=lambda x:x[0].lower())
            for element in subdomains_alphabetically_sorted:
                report_file.write(f'{element[0]}: {element[1]}\n')
            
            report_file.close()
    

