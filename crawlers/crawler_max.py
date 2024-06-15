import asyncio
import json
import os.path
import logging
from pyppeteer import launch
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


async def extract_html_with_pyppeteer(url, html_file_path):
    """
    crawl an url and create a html file with the content of a given url.
    :param url: the url to crawl
    :return: None
    """
    browser = await launch(headless=True,
                           executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
    page = await browser.newPage()

    await page.goto(url, {'waitUntil': 'networkidle2'})

    async def click_load_more_button():
        try:
            load_more_button = await page.xpath(
                '//span[contains(@class, "load-more-benefits") and contains(text(), "לכל ההטבות")]')
            if load_more_button:
                await load_more_button[0].click()
                await asyncio.sleep(2)  # Wait for new content to load
                return True
            return False
        except Exception as e:
            print(f"Error clicking 'Load More' button: {e}")
            return False

    while await click_load_more_button():
        logger.info('Clicked "Load More" button, loading more content...')

    try:
        await page.waitForSelector('.benfit-link',
                                   {'timeout': 10000})  # Adjust the selector and timeout as needed
    except Exception as e:
        print(f"Error waiting for selector: {e}")

    await asyncio.sleep(5)

    html = await page.content()

    with open("max_benefits\\" + html_file_path, 'w', encoding='utf-8') as f:
        f.write(html)

    await browser.close()


def extract_sub_benefits(html_content: str, url_to_join: str) -> list[dict]:
    """
    Parse the HTML content to extract sub-benefits of a category.

    :param html_content: The HTML content to parse.
    :param url_to_join: The base URL to join with relative links of a benefit.
    :return: A list of dictionaries containing the extracted data.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    sub_benefits_divs = soup.find_all('div', class_='sub-benfits ng-star-inserted')

    extracted_data = []
    for div in sub_benefits_divs:
        benefit_name = div.find('h2').get_text(strip=True) if div.find('h2') else None
        benefit_details = div.find('p', class_='text').get_text(strip=True) if div.find('p',
                                                                                        class_='text') else None
        benefit_link = div.find('a', class_='benfit-link') if div.find('a', class_='benfit-link') else None
        if benefit_link and 'href' in benefit_link.attrs:
            benefit_link = benefit_link['href']
        else:
            continue
        extracted_data.append({
            'benefit_name': benefit_name,
            'benefit_details': benefit_details,
            'benefit_link': urljoin(url_to_join, benefit_link) if benefit_link else None
        })
    return extracted_data


def crawl(crawl_url: str, html_path="none.html", crawl=False):
    """
    Crawl a category to extract sub-benefits data and save into a JSON file.
    :param crawl_url: the full url of the category to crawl
    :param html_path: the path to the html file to read from or to create
    :param crawl: should the function crawl the page or not (use a html file)
    :return: List of benefits
    """
    if crawl or os.path.exists("max_benefits\\" + html_path) is False:
        asyncio.run(extract_html_with_pyppeteer(crawl_url, html_path))
    par_path = os.path.abspath(os.path.join(os.path.curdir, os.pardir))
    with open(par_path + "\\max_benefits\\" + html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    benefits = extract_sub_benefits(html_content, crawl_url)
    with open(par_path + "\\max_benefits\\" + html_path.split(".")[0] + ".json", 'w', encoding='utf-8') as f:
        json.dump(benefits, f, ensure_ascii=False, indent=4)
    return benefits


async def get_sub_categories(main_url="https://www.max.co.il/benefits"):
    """
    Extract the sub-categories URLs from the main benefits page.
    :param main_url: the main benefits page URL
    :return: a list of sub-categories URLs
    """
    browser = await launch(headless=True,
                           executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
    page = await browser.newPage()
    await page.goto(main_url, {'waitUntil': 'networkidle2'})

    try:
        await page.waitForSelector('.more-benfits.ng-star-inserted', {'timeout': 10000})

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        sub_categories_divs = soup.find_all('div', class_='more-benfits ng-star-inserted')

        links = []
        for div in sub_categories_divs:
            anchor_tag = div.find('a', class_='link arrow-link')
            if anchor_tag and 'href' in anchor_tag.attrs:
                links.append(anchor_tag['href'])

    except Exception as e:
        print(f"An error occurred: {e}")
        html = await page.content()
        links = []

    await browser.close()

    return links


def start_crawling(main_url="https://www.max.co.il/benefits"):
    links = asyncio.run(get_sub_categories(main_url))
    cnt = 0
    for link in links:
        # print(f'Crawling sub-category: {link}')
        print(urljoin(main_url, link), f'{link.split("/")[-1]}.html')
        cnt += len(crawl(urljoin(main_url, link), f'{link.split("/")[-1]}.html', crawl=False))
    # print(f"Number of benefits crawled: {cnt}")


if __name__ == '__main__':
    main_url = "https://www.max.co.il/benefits"
    start_crawling(main_url)
