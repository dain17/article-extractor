import datetime
import re
import os
import time
from selenium.webdriver.common.by import By

from sites.domain import Domain
from sites.library import query_selector, query_selector_all, safed_query_selector
from sites.perhaps import Perhaps


class Yahoo(Domain):

    def __init__(self, category):
        self.category = category or 'science'
        self.main_page = {
            'science': 'https://news.yahoo.co.jp/categories/science',
            'it': 'https://news.yahoo.co.jp/categories/it'
        }[self.category]

    def extract_article_URLs(self, elem, old_urls):
        return [e.get_attribute('href') for e in query_selector_all(elem, 'a.newsFeed_item_link')]

    # next page
    def open_next_page(self, driver):
        query_selector(driver, '.newsFeed_more > button').click()

    def get_output_dir(self):
        return os.path.join('yahoo', self.category, self.article_id)

    def set_article_url(self, article_url):
        self.article_url = article_url
        self.comment_url = re.sub('/$', '', article_url.split('?')[0]) + '/comments/'
        self.article_id = re.sub('/$', '', article_url).split('/')[-1]

    # main extraction function
    def extract_article(self, article_url, driver):
        article_info = self.extract_article_json(driver=driver)
        article_text = self.extract_article_context(driver=driver)
        comments = self.extract_comments(driver=driver)

        article_info['comment_count'] = len([r for r in comments]) + len([c for root in comments for c in root['replies']])

        return article_info, article_text, comments

    def extract_article_json(self, driver):
        page_items = query_selector_all(driver, '#contentsWrap .pagination_item')

        # title: string, max_page: int, published_date: string, extracted_date: time, can_comment: bool, author: string, author_url: string
        # +comment_count: int
        return {
            'title': query_selector(driver, '#contentsWrap header h1').text,
            'max_page': int(page_items[-2].text) if len(page_items) > 0 else 1,
            'published_date': query_selector(driver, '#contentsWrap header time').text,
            'extracted_date': datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'can_comment': safed_query_selector(driver, '#articleCommentModule').exists(),
            'author': (query_selector_all(driver, '#contentsWrap article header a[href^="/byline"]') + query_selector_all(driver, '#contentsWrap article footer a'))[0].text,
            'comment_count': 0
        }

    def extract_article_context(self, driver):
        url = Perhaps([self.article_url])
        article_context = ''
        while(url.exists()):
            print('access to: ' + url.get())
            driver.get(url.get())
            article_context += query_selector(driver, '.article_body, .articleBody').text
            url = Perhaps([e.get_attribute('href') for e in query_selector_all(driver, '.pagination_item-next:not(.pagination_item-disabled) > a')])

        return article_context

    def extract_comments(self, driver):
        url = Perhaps([self.comment_url])
        comments = []
        while(url.exists()):
            print('access to: ' + url.get())
            driver.get(url.get())
            # iframe = safed_query_selector(driver, '.news-comment-plguin-iframe')
            # print(iframe.l)
            # if iframe.is_empty():
            #     break
            # driver.switch_to.frame(iframe.get())

            # open reply items
            # for e in query_selector_all(driver, '.btnView'):
            buttons = query_selector_all(driver, 'button[class^="UserCommentItem__ExpandReplyComment-"]:first-child')
            for e in [b for b in buttons if query_selector(b, 'span[class^="UserCommentItem__ReplyCount-"]').get_attribute('textContext') != '0']:
                time.sleep(0.25)
                e.click()

            buttons = query_selector_all(driver, 'div[class^="MoreButton__CommentMore-"] button')
            while len(buttons) > 0:
                for e in buttons:
                    time.sleep(0.25)
                    e.click()
                buttons = query_selector_all(driver, 'div[class^="MoreButton__CommentMore-"] button')

            # for comment_elem in query_selector_all(driver, '#comment-list-item > li'):
            for comment_elem in query_selector_all(driver, '.viewableWrap > ul:nth-last-child(4) > li'):
                comment_data = self.extract_comment_json(comment_elem)
                # comment_data['replies'] = [self.extract_comment_json(reply) for reply in query_selector_all(comment_elem, '.responseItem article')]
                comment_data['replies'] = [self.extract_comment_json(reply) for reply in query_selector_all(comment_elem, 'li[class^="ReplyCommentItem__Item-"]')]
                comments.append(comment_data)

            url = Perhaps([e.get_attribute('href') for e in query_selector_all(driver, '.pagination_item-next:not(.pagination_item-disabled) a')])

        return comments

    def extract_comment_json(self, elem):
        # user_name: string, user_url: string, time: string, context: string, good: int, bad: int
        return {
            'user_name': query_selector(elem, 'h2 > a[href^="https://news.yahoo.co.jp/profile/id/"]').text,
            'user_url': query_selector(elem, 'h2 > a[href^="https://news.yahoo.co.jp/profile/id/"]').get_attribute('href'),
            'time': query_selector(elem, 'time').get_attribute('textContext'),
            'context': query_selector(elem, 'p[class*="CommentItem__Comment-"]').text,
            'good': int(query_selector(elem, 'button:nth-child(2) span[class^="ThumbsUpButton__ThumbsupCount-"]').text),
            'bad': int(query_selector(elem, 'button:nth-child(2) span[class^="ThumbsDownButton__ThumbsdownCount-"]').text)
        }
