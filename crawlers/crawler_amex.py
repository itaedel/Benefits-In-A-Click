import json
import os.path
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl_category(category_url):
    """
    Crawl a category page
    :param category_url: url of the category page
    :return: list of benefit pages
    """
    try:
        response = requests.get(category_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            benefits = []
            sub_benefits_a = soup.find_all('a', class_=lambda x: x and 'category-item' in x.split())
            for a_obj in sub_benefits_a:
                benefit_name = a_obj.find('div', class_='text-overflow caption-title txtBold').get_text(
                    strip=True)
                benefit_details = (a_obj.find('div', class_='text-overflow caption-sub-title')).get_text(
                    strip=True)
                benefit_link = urljoin(category_url, a_obj['onclick'].split("location.href='")[1].strip("\'"))
                benefits.append({
                    'benefit_name': benefit_name,
                    'benefit_details': benefit_details,
                    'benefit_link': benefit_link
                })
            return benefits
        return []
    except Exception as e:
        print("Error crawling category:", e)
        return []



def extract_categories(base_url):
    """
    Go over base_url and extract all the categories
    :param base_url: base url to crawl from
    :return: list of full links of categories
    """
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            categories_title_row = soup.find_all('div', class_='category-title row')
            categories = []
            for title_row in categories_title_row:
                a_tag = title_row.find('a', role='link')
                if a_tag:
                    category_url = re.search(r"partialPagesHandler.categoryTextClick\('([^']*)'", a_tag['onclick'])
                    category_name = title_row.find('h2').get_text(strip=True)
                    categories.append(
                        {'category_name': category_name,
                         'category_url': urljoin(base_url, category_url.group(1))})
            return categories
        return []
    except Exception as e:
        print("Error extracting categories:", e)
        return []


def start_crawling():
    """
    Start the crawling processד
    :return:
    :rtype:
    """
    start_url = 'https://rewards.americanexpress.co.il/'
    categories = extract_categories(start_url)
    par_path = os.path.abspath(os.path.join(os.path.curdir, os.pardir))
    cnt = 0
    for category in categories:
        def sanitize_filename(cat_name):
            invalid = '<>:"/\\|?*'
            for char in invalid:
                cat_name = cat_name.replace(char, '')  # You can replace with an underscore '_' if preferred
            return cat_name
        #print("Crawling category:", category['category_name'])
        category['category_name'] = sanitize_filename(category['category_name'])
        cat = crawl_category(category['category_url'])
        cnt += len(cat)
        if not os.path.exists(par_path + '\\amex_benefits'):
            os.makedirs(par_path + '\\amex_benefits')
        with open(par_path + '\\amex_benefits\\' + category['category_name'] + '.json', 'w') as f:
            json.dump(cat, f, ensure_ascii=False, indent=4)
    #print("Number of benefits crawled:", cnt)

if __name__ == '__main__':
    start_crawling()
