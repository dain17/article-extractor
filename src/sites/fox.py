import datetime
import os
import re
from time import sleep

from sites.domain import Domain
from sites.library import query_selector, query_selector_all, safed_query_selector

exclusive_url = {'https://www.foxnews.com/science/james-webb-space-telescope-full-color-images'}
# exclusive_url = {}


class Fox(Domain):

    def __init__(self, category):
        self.category = category or 'drones'
        self.main_page = {
            'science': 'https://www.foxnews.com/science',
            'drones': 'https://www.foxnews.com/category/tech/technologies/drones',
            'tech': 'https://www.foxnews.com/category/tech',
            'economy': 'https://www.foxnews.com/category/us/economy',
            # world
            'un': 'https://www.foxnews.com/category/world/united-nations',
            'conflicts': 'https://www.foxnews.com/category/world/conflicts',
            'terrorism': 'https://www.foxnews.com/category/world/terrorism',
            'disasters': 'https://www.foxnews.com/category/world/disasters',
            'global-economy': 'https://www.foxnews.com/category/world/global-economy',
            'environment': 'https://www.foxnews.com/category/world/environment',
            'religion': 'https://www.foxnews.com/category/world/religion',
            'scandals': 'https://www.foxnews.com/category/world/scandals',
            # health
            'coronavirus': 'https://www.foxnews.com/category/health/infectious-disease/coronavirus',
            'healthy-living': 'https://www.foxnews.com/category/health/healthy-living',
            'medical-research': 'https://www.foxnews.com/category/health/medical-research',
            'mental-health': 'https://www.foxnews.com/category/health/mental-health',
            'cancer': 'https://www.foxnews.com/category/health/cancer',
            'heart-health': 'https://www.foxnews.com/category/health/heart-health',
            'childrens-health': 'https://www.foxnews.com/category/health/healthy-living/childrens-health'
        }[self.category]

        # document.querySelector('button.pf-widget-close').click()

    def extract_article_URLs(self, driver, old_urls):
        sleep(0.5)
        self.try_closing_advatisement(driver=driver)
        articles = [a for a in query_selector_all(driver, '.collection-article-list article.article') if query_selector(a, '.eyebrow').get_attribute('innerText') != 'VIDEO']
        article_urls = [query_selector(a, 'div.m > a').get_attribute('href') for a in articles]
        return [('https://www.foxnews.com' if 'https://' not in url else '') + url for url in article_urls if url not in exclusive_url]

    def open_next_page(self, driver):
        for i in range(10):
            self.click(driver, query_selector(driver, 'div.js-load-more a'), sleep_count=3)
        print('open next page * 10')
    
    def get_output_dir(self):
        return os.path.join('fox', self.category, self.article_id)
    
    def set_article_url(self, article_url):
        self.article_url = article_url
        self.article_id = re.sub('/$', '', article_url).split('/')[-1]
        self.comment_count = 0
        self.comment_iter = 0
        self.comments = []
        self.are_no_replies = None


    def extract_article(self, article_url, driver):
        print(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), article_url)
        self.try_closing_advatisement(driver=driver)

        if safed_query_selector(driver, '.collection-article-list article.article').exists():
            print(f'error: {article_url}')
            return {}, '', [], 1

        article_info = self.extract_article_json(driver=driver)
        article_text = '\n\n'.join([p.get_attribute('innerText') for p in query_selector_all(driver, '.article-body > p') if not p.get_attribute('innerText').isupper() and not safed_query_selector(p, 'strong').exists()])
        finished_comment_set, finished_root_keys, show_more_count = set(), set(), 0
        sort_by = 'oldest'

        while True:
            self.comment_count += self.comment_iter
            self.comment_iter = 0

            # scrolling to comments
            comment_element = safed_query_selector(driver, '#comments')
            if comment_element.exists():
                driver.execute_script('arguments[0].scrollIntoView({"behavior": "instant"})', comment_element.get())
                sleep(10)
            else:
                return article_info, article_text, [], 0

            shadow_root = query_selector(driver, '#comments div[data-labels-section]').shadow_root

            if self.are_no_replies is None:
                comment_count_element = safed_query_selector(shadow_root, 'span[data-spot-im-class="comments-count"]')
                comment_count_text = comment_count_element.get().get_attribute('innerText') if comment_count_element.exists() else '0 Comment'
                article_info['real_comment_count'] = re.match(r'(.*) Comment', comment_count_text).group(1)
                comment_count = float(article_info['real_comment_count'][:-1].strip()) * 1000 if article_info['real_comment_count'][-1] == 'K' else int(article_info['real_comment_count'])
                self.are_no_replies = article_info['are_no_replies'] = 500 < comment_count
                print(f'No replies: {self.are_no_replies}, Comment count text: {comment_count_text}, Comment count: {comment_count}')
                if comment_count == 0:
                    return article_info, article_text, [], 0

            # ordering comments by oldest
            self.click(driver, query_selector(shadow_root, '#spotim-sort-by'), sleep_count=1)
            ordering_shadowroot = query_selector(driver, 'body > div[data-spot-im-shadow-host]').shadow_root
            self.click(driver, query_selector(ordering_shadowroot, f'button[data-spmark="{sort_by}"]'))

            # closing adsense
            # adsense_movie = safed_query_selector(driver, '.close')
            # adsense_movie.exists() and self.click(driver, adsense_movie.get())
            for adsense in query_selector_all(driver, '.close'):
                self.click(driver, adsense, sleep_count=0.5)

            # click show more
            if self.are_no_replies == False:
                for i in range(show_more_count):
                    show_more = query_selector(shadow_root, 'button[aria-label="Show more comments"]')
                    self.click(driver, show_more, sleep_count=3)
            
            if show_more_count != 0:
                finished_comment_set = set(query_selector_all(shadow_root, 'article.spcv_root-message > div > div.spcv_message-stack'))
                show_more = safed_query_selector(shadow_root, 'button[aria-label="Show more comments"]')
                show_more.exists() and self.click(driver, show_more.get(), sleep_count=5)
                print('/', end='')
            
            while True:
                all_comment_set = set(query_selector_all(shadow_root, 'article.spcv_root-message > div > div.spcv_message-stack'))
                new_comment_set = all_comment_set - finished_comment_set
                new_comments_json = [comment for e in new_comment_set if 'error' in (comment := self.extract_comment_json(e, driver, 1)) or self.create_key(comment) not in finished_root_keys]
                self.comments += new_comments_json
                finished_comment_set = all_comment_set
                new_root_keys = {self.create_key(j) for j in new_comments_json if 'error' not in j}
                is_deprecated = len(finished_root_keys.intersection(new_root_keys)) > 0 and self.comment_count > 250
                finished_root_keys |= new_root_keys

                show_more = safed_query_selector(shadow_root, 'button[aria-label="Show more comments"]')

                if self.comment_iter > 250:
                    break

                if show_more.is_empty() or 500 < self.comment_count + self.comment_iter or (self.are_no_replies and is_deprecated):
                    article_info['comment_count'] = self.count_comment(self.comments)
                    print(show_more.is_empty(), 500 < self.comment_count + self.comment_iter, self.are_no_replies and is_deprecated)
                    return article_info, article_text, self.comments, 0

                print('/', end='', flush=True)
                show_more_count += 1
                driver.execute_script('arguments[0].scrollIntoView({"behavior": "instant"})', show_more.get())
                sleep(1)
                self.click(driver, show_more.get(), sleep_count=5)

            sort_by = 'newest' if self.are_no_replies else 'oldest'
            driver.refresh()
            sleep(5)

    def extract_article_json(self, driver):

        author = safed_query_selector(driver, '.author-byline > span > span > a')
        if (author.is_empty()):
            author = safed_query_selector(driver, '.author-byline > span > a')
        if (author.is_empty()):
            author_name = safed_query_selector(driver, '.author-byline > span > span')
            author_name = author_name.get().text if author_name.exists() else ''

        subtitle = safed_query_selector(driver, '.sub-headline')

        return {
            'URL': self.article_url,
            'title': query_selector(driver, '.headline').text,
            'subtitle': subtitle.get().text if subtitle.exists() else '',
            'published_date': query_selector(driver, '.article-date time').text,
            'extracted_date': datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'author_name': author.get().text if author.exists() else author_name,
            'author': author.get().get_attribute('href') if author.exists() else '',
            'are_no_replies': False, # initialized in extract_article
            'comment_count': 0, # added later
            'real_comment_count': '' # initialized in extract_article
        }

    def extract_comment_json(self, elem, driver, level):
        # See more own text
        see_more = safed_query_selector(elem, ':scope > div div[data-spot-im-class="message-text"] > span')
        see_more.exists() and self.click(driver=driver, element=see_more.get(), sleep_count=1)

        # open replies
        show_replies_item = safed_query_selector(elem, ':scope > div.spcv_show-more-replies > button')
        while(show_replies_item.exists() and not self.are_no_replies):
            num = int(re.findall(r'\d+', show_replies_item.get().get_attribute('innerText'))[0])
            self.click(driver, show_replies_item.get())
            if num >= 5:
                show_replies_item = safed_query_selector(elem, ':scope > div.spcv_show-more-replies > button')
            else:
                break

        try:
            user_name = query_selector(elem, ':scope > div span[data-spot-im-class="message-username"]').text
            posted_time = query_selector(elem, ':scope > div time[data-spot-im-class="message-timestamp"]').text
            context = query_selector(elem, ':scope > div div[data-spot-im-class="message-text"]').text
        except Exception as e:
            print('e', end='')
            return {
                'error': 'error'
            }

        good = safed_query_selector(elem, ':scope > div button[aria-label="Vote Up"] span.components-MessageActions-components-VoteButtons-index__votesCounter')
        bad = safed_query_selector(elem, ':scope > div button[aria-label="Vote Down"] span.components-MessageActions-components-VoteButtons-index__votesCounter')
        replies = query_selector_all(elem, ':scope > ul.spcv_children-list > li > div > div.spcv_message-stack') if not self.are_no_replies else []
        replies_json = [self.extract_comment_json(c, driver, level + 1) for c in replies]

        self.comment_iter += 1
        print('.', end='')
        if (self.comment_count + self.comment_iter) % 100 == 0:
            print(self.comment_count + self.comment_iter)

        return {
            'user_name': user_name,
            'time': posted_time,
            'context': context,
            'good': good.get().text if good.exists() else '0',
            'bad': bad.get().text if bad.exists() else '0',
            'replies': replies_json
        }

    def try_closing_advatisement(self, driver):
        ad = safed_query_selector(driver, 'button.pf-widget-close')
        ad.exists() and self.click(driver, ad.get())
    
    def click(self, driver, element, sleep_count=2):
        driver.execute_script('arguments[0].click();', element)
        sleep(sleep_count)

    def create_key(self, root_json):
        return f'{root_json["user_name"]}::{root_json["context"]}'

    def count_comment(self, comments_list):
        return sum([self.count_comment(c['replies']) for c in comments_list if 'error' not in c], len(comments_list))
