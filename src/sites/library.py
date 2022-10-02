from selenium.webdriver.common.by import By

from sites.perhaps import Perhaps

def query_selector(element, query: str):
    return element.find_element(by=By.CSS_SELECTOR, value=query)

def query_selector_all(element, query: str):
    return element.find_elements(by=By.CSS_SELECTOR, value=query)

def safed_query_selector(element, query: str):
    return Perhaps(query_selector_all(element=element, query=query))