# Author: Your Name
# Date: 18/03/2024
# Description:
#   This is a web-crawler for the Isracard benefits website.

# create a web crawler using beautiful soup
import json
import os.path
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl_category(url):
    """
    Crawl a category to extract sub-benefits data.
    :param url: the category url to crawl
    :return:
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sub_benefits_a = soup.find_all('a', class_=lambda x: x and 'category-item' in x.split())
            benefits = []
            for a_obj in sub_benefits_a:
                benefit_name = a_obj.find('div', class_='text-overflow caption-title txtBold').get_text(
                    strip=True)
                benefit_details = (a_obj.find('div', class_='text-overflow caption-sub-title')).get_text(
                    strip=True)
                benefit_link = urljoin(url, a_obj['onclick'].split("location.href='")[1].strip("\'"))
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
                    category_url = re.search(r"partialPagesHandler.categoryTextClick\('([^']*)'",
                                             a_tag['onclick'])
                    category_name = title_row.find('h2').get_text(strip=True)
                    categories.append(
                        {'category_name': category_name,
                         'category_url': (base_url + category_url.group(1))})
            return categories
        return []
    except Exception as e:
        print("Error extracting categories:", e)
        return []


def start_crawling():
    start_url = 'https://benefits.isracard.co.il/'
    categories = extract_categories(start_url)
    par_path = os.path.abspath(os.path.join(os.path.curdir, os.pardir))
    cnt = 0
    for category in categories:
        def sanitize_filename(cat_name):
            invalid = '<>:"/\\|?*'
            for char in invalid:
                cat_name = cat_name.replace(char, '')  # You can replace with an underscore '_' if preferred
            return cat_name

        # print("Crawling category:", category['category_name'])
        category['category_name'] = sanitize_filename(category['category_name'])
        cat = crawl_category(category['category_url'])
        cnt += len(cat)
        with open(par_path + "\\isracard_benefits\\" + category['category_name'] + '.json', 'w',
                  encoding='utf-8') as f:
            json.dump(cat, f, ensure_ascii=False, indent=4)
    # print("Number of benefits crawled:", cnt)


if __name__ == '__main__':
    start_crawling()
