import os
import re
import psycopg2
import json

abroad = "abroad"
shopping = "shopping"
entertainment = "entertainment"
food = "food"
attractions = "attractions"
category_dict = {food: "אוכל,מסעדה,מסעדות,ארוחה,ארוחות,טעימה,טעימות,שתייה",
                 abroad: "טיסות,חוץ לארץ,טיסה,חו\"ל,מלון,מלונות,צימר,השכרת רכב,ביטוח נסיע",
                 shopping: "קניות,קנייה,קניה,קניון,שופינג,חנות,חנויות,קאשבק,קשבאק",
                 entertainment: "בילוי,פנאי,קולנוע,מופע,הופעה,מוזיקה,סטנדאפ,ביליארד,קזינו,קזינואים,פאב,בר,קפה,סרט,קולנוע,סינמה,מחזמר,תיאטרון",
                 attractions: "אטרקציה,אטרקציות,פארק,מוזיאון,מוזאון,סיור,מוזיאונים,סדנה,טיול"}


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


def extract_category_from_benefit(benefit_name, benefits_details) -> str:
    chars_del = ".,:;\"'!?-"
    trans_table = str.maketrans('', '', chars_del)
    for category in category_dict:
        for word in category_dict[category].split(','):
            word_pattern = re.compile(r'.*' + re.escape(word) + r'.*')
            if word_pattern.search(benefit_name.translate(trans_table)) or \
                    word_pattern.search(benefits_details.translate(trans_table)):
                return category
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
    print(f"Loading data from {benefits_folder} to {table_name}")
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (latest_time TIMESTAMP, url VARCHAR UNIQUE, "
                "benefit_name VARCHAR, benefit_details VARCHAR, category VARCHAR, "
                "PRIMARY KEY (latest_time, url))")
    cur.execute(f"DELETE FROM {table_name}")
    for file_name in os.listdir(benefits_folder):
        if file_name.endswith('.json'):
            with open(benefits_folder + '\\' + file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for entry in data:
                url = entry.get('benefit_link', None)
                benefit_name = entry.get('benefit_name', None).translate(str.maketrans('', '', "'"))
                benefit_details = entry.get('benefit_details', None)
                category = get_category(categories_dict, file_name)
                if category == "":
                    category = extract_category_from_benefit(benefit_name, benefit_details)
                cur.execute(
                    f"INSERT INTO {table_name} (latest_time, url, benefit_name, benefit_details, category)"
                    " VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s)"
                    "ON CONFLICT (url) DO NOTHING",
                    (url, benefit_name, benefit_details, category))
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    print(f"number of {table_name} rows:", len(rows))


def open_db_conn(real_db=False):
    """
    open the connection to the DB
    :return: cursor and connection
    """
    if real_db:
        # removed the actual connection details for security reasons
        pass
    else:
        # change to your local db
        conn = psycopg2.connect(
            dbname="",
            user="",
            password="",
            host="",
            port="",
            options="-c client_encoding=UTF8"
        )
    print("Connected to the database")
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


def queires(cur):
    cur.execute("SELECT * FROM benefits_isracard")
    rows = cur.fetchall()
    with open('isracard_rows.txt', 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(str(row) + '\n')
    cur.execute("SELECT * FROM benefits_max")
    rows = cur.fetchall()
    with open('max_rows.txt', 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(str(row) + '\n')
    cur.execute("SELECT * FROM benefits_amex")
    rows = cur.fetchall()
    with open('amex_rows.txt', 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(str(row) + '\n')
    print("Done writing rows")


def crawl_all(max_crawl=True, isracard_crawl=True, amex_crawl=True):
    if isracard_crawl:
        from crawlers import crawler_isracard
        print("Crawling isracard")
        crawler_isracard.start_crawling()
    if max_crawl:
        from crawlers import crawler_max

        print("Crawling max")
        crawler_max.start_crawling()
    if amex_crawl:
        from crawlers import crawler_amex

        print("Crawling amex")
        crawler_amex.start_crawling()


def load_all_data(load_real_db=False):
    cur, conn = open_db_conn(load_real_db)
    isracard_categories_dict = {"נוסעים לחול": abroad, "אטרקציות": attractions,
                                "בילוי ופנאי": entertainment,
                                "הטבות אונליין": shopping}
    load_data(isracard_categories_dict, 'isracard_benefits', 'benefits_isracard', cur)

    max_categories_dict = {"abroadbenefits": abroad, "attractions": attractions, "fashion": shopping,
                           "online": shopping, "movies": entertainment, "musicshows": entertainment,
                           "plays": entertainment, "standupshows": entertainment, "vacation": abroad,
                           "tastytreat": food}
    load_data(max_categories_dict, 'max_benefits', 'benefits_max', cur)

    amex_categories_dict = {"נופש וחול": abroad, "קניות": shopping, "תרבות ופנאי": entertainment,
                            "קולנוע": entertainment, "מופעי סטנדאפ": entertainment,
                            "מסעדות ובתי קפה": food}
    load_data(amex_categories_dict, 'amex_benefits', 'benefits_amex', cur)
    queires(cur)
    cur.close()
    conn.close()


if __name__ == '__main__':
    crawl_all()
    load_all_data(load_real_db=False)  # real-db isn't used for security reasons
    print("Done")
