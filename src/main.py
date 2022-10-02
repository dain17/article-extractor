import argparse
import os
import json
import atexit
from time import sleep
from selenium import webdriver

from sites.factory import create_domain_instance


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--domain', help='Domain where you extract articles and comments.', type=str, default='yahoo')
    parser.add_argument('-c', '--category', help='News Category', type=str)
    parser.add_argument('-n', '--num', help='Number of times to extract.', type=int, default=10)
    parser.add_argument('-o', '--output', help='Output folder', type=str, default='./articles/')

    args = parser.parse_args()
    domain = create_domain_instance(domain=args.domain, category=args.category)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--remote-debugging-port=9222')
    options.set_capability("loggingPrefs", {'performance': 'ALL'})

    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=options,
    )
    atexit.register(lambda: driver.quit())
    driver.set_window_size(950, 800)

    urls, now = [], 0
    driver.get(domain.main_page)

    while now < args.num:
        if now != 0:
            domain.open_next_page(driver)

        urls = domain.extract_article_URLs(driver, urls)
        driver.execute_script('window.open();')
        driver.switch_to.window(driver.window_handles[1])
        first = now

        for article_url in urls[first:args.num]:
            now += 1

            domain.set_article_url(article_url=article_url)
            if os.path.isfile(os.path.join(args.output, domain.get_output_dir(), 'info.json')):
                print(f'skipped: {domain.get_output_dir()}')
                continue

            os.makedirs(os.path.join(args.output, domain.get_output_dir()), exist_ok=True)
            driver.get(article_url)
            article_info, article_text, comments, status_code = domain.extract_article(driver=driver, article_url=article_url)
            
            if status_code != 0:
                continue

            with open(os.path.join(args.output, domain.get_output_dir(), 'article.txt'), 'w') as f:
                f.write(article_text)

            with open(os.path.join(args.output, domain.get_output_dir(), 'comments.json'), 'w') as f:
                json.dump(comments, f, indent=4, ensure_ascii=False)

            with open(os.path.join(args.output, domain.get_output_dir(), 'info.json'), 'w') as f:
                json.dump(article_info, f, indent=4, ensure_ascii=False)

        driver.execute_script('window.close();')
        driver.switch_to.window(driver.window_handles[0])
        sleep(5)


if __name__ == '__main__':
    main()
