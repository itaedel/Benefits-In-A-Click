import os

import psycopg2
import json

abroad = "abroad"
shopping = "shopping"
entertainment = "entertainment"
food = "food"
attractions = "attractions"


def get_category(categories_dict: dict, file_name: str) -> str:
    """
    Get the category of the file according to the dictionary (might not exist).
    :param categories_dict: dictionary of categories
    :param file_name: the name of the file including file type
    :return: category of the file
    """
    if file_name.split('.')[0] in categories_dict:
        return categories_dict[file_name.split('.')[0]]
    return ""


def load_data(categories_dict: dict, benefits_folder: str, table_name: str, cur) -> None:
    """
    Load the data from the json files into the database.
    :param categories_dict: translates JSON filename into category
    :param benefits_folder:
    :param table_name: the name of the table
    :param cur: cursor to the database
    :return: None
    """
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (latest_time TIMESTAMP, url VARCHAR UNIQUE, "
                "benefit_name VARCHAR, benefit_details VARCHAR, category VARCHAR, "
                "PRIMARY KEY (latest_time, url))")
    cur.execute(f"DELETE FROM {table_name}")
    for file_name in os.listdir(benefits_folder):
        if file_name.endswith('.json'):
            with open(benefits_folder + '\\' + file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            category = get_category(categories_dict, file_name)
            for entry in data:
                url = entry.get('benefit_link', None)
                benefit_name = entry.get('benefit_name', None)
                benefit_details = entry.get('benefit_details', None)
                cur.execute(
                    f"INSERT INTO {table_name} (latest_time, url, benefit_name, benefit_details, category)"
                    " VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s)"
                    "ON CONFLICT (url) DO NOTHING",
                    (url, benefit_name, benefit_details, category))
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    print(f"number of {table_name} rows:", len(rows))


def open_db_conn():
    """
    open the connection to the DB
    :return: cursor and connection
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432",
        options="-c client_encoding=UTF8"
    )
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


if __name__ == '__main__':
    crawl_all = True
    max_crawl = True
    isracard_crawl = True
    amex_crawl = True
    cur, conn = open_db_conn()
    if isracard_crawl or crawl_all:
        from crawlers import crawler_isracard

        print("Crawling isracard")
        crawler_isracard.start_crawling()
        isracard_categories_dict = {"נוסעים לחול": abroad, "אטרקציות": attractions,
                                    "בילוי ופנאי": entertainment,
                                    "הטבות אונליין": shopping}
        load_data(isracard_categories_dict, 'isracard_benefits',
                  'benefits_isracard', cur)
    if max_crawl or crawl_all:
        from crawlers import crawler_max

        print("Crawling max")
        crawler_max.start_crawling()
        max_categories_dict = {"abroadbenefits": abroad, "attractions": attractions, "fashion": shopping,
                               "online": shopping, "movies": entertainment, "musicshows": entertainment,
                               "plays": entertainment, "standupshows": entertainment, "vacation": abroad,
                               "tastytreat": food}
        load_data(max_categories_dict, 'max_benefits', 'benefits_max', cur)
    if amex_crawl or crawl_all:
        from crawlers import crawler_amex

        print("Crawling amex")
        crawler_amex.start_crawling()
        amex_categories_dict = {"נופש וחול": abroad, "קניות": shopping, "תרבות ופנאי": entertainment,
                                "קולנוע": entertainment, "מופעי סטנדאפ": entertainment,
                                "מסעדות ובתי קפה": food}
        load_data(amex_categories_dict, 'amex_benefits', 'benefits_amex', cur)
    cur.close()
    conn.close()
