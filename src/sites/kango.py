import os
import re
import time
import sys
from sites.domain import Domain
from sites.library import query_selector, query_selector_all, safed_query_selector
from sites.perhaps import Perhaps


class Kango(Domain):
    def __init__(self, category) -> None:
        self.hub_id = category or '101'
        self.article_id = 0
        self.main_page = 'https://www.kango-roo.com/kokushi/kako/' + self.hub_id

    def extract_article_URLs(self, elem, old_urls):
        return old_urls + [e.get_attribute('href') for e in query_selector_all(elem, '.questionList a')]

    def open_next_page(self, driver):
        print('open_next_page')
        probrems = query_selector_all(driver, '.whiteBox li')
        optional_url = Perhaps([query_selector(e, 'a').get_attribute('href') for i, e in enumerate(probrems[1:]) if probrems[i].get_attribute('class') == 'current'])
        if optional_url.is_empty():
            print('finish')
            sys.exit()
        
        self.hub_id = optional_url.get()[-4:-1]
        self.main_page = 'https://www.kango-roo.com/kokushi/kako/' + self.hub_id
        driver.get(self.main_page)
        self.article_id = 0
        time.sleep(0.5)

    def get_output_dir(self):
        return os.path.join('kango', self.hub_id, str(self.article_id))

    def set_article_url(self, article_url):
        self.article_url = article_url
        self.article_id += 1
        
    def extract_article(self, article_url, driver):
        print(f'{self.hub_id} {self.article_id} access to: {article_url}')
        information = self.extract_info_json(driver=driver)
        context = '\n\n'.join(information.values())

        return information, context, [], 0

    def extract_info_json(self, driver):
        text = ''

        choices = safed_query_selector(driver, '.choices')
        answers = query_selector_all(driver, '.answerBox .clearfix dt')
        answer_details = query_selector_all(driver, '.answerBox .clearfix dd')
        detail = '\n'.join([e.get_attribute('innerText') for e in query_selector_all(driver, '.answerBox > p:not(.title)')])

        for i, e in enumerate(answers):
            text += '○ ' if safed_query_selector(e, '.correct').exists() else '× '
            text += e.get_attribute('innerText').strip() + '\n'
            text += answer_details[i].get_attribute('innerText').strip() + '\n'

        if len(answers) == 0:
            text += query_selector(driver, '.answerBox .flex-row').get_attribute('innerText').strip().replace('\n\t\t\t\t\t\t\t\t\t', ' ')

        return {
            'question': query_selector(driver, '.questionText').get_attribute('innerText'),
            'choices': choices.get().get_attribute('innerText') if choices.exists() else '',
            'answers': text,
            'detail': detail
        }

    def trim(self, input):
        return re.sub('\t*', '', input)
        