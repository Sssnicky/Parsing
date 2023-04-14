import json
import requests
import re
from fake_headers import Headers
from bs4 import BeautifulSoup


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def find_companies():
    parsed_data = []
    hh_main_html = requests.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2",
                                headers=get_headers()).text
    hh_main_soup = BeautifulSoup(hh_main_html, "lxml")

    tag_all_articles = hh_main_soup.find("main", class_="vacancy-serp-content")
    articles_tags = tag_all_articles.find_all("div", class_="vacancy-serp-item-body__main-info")

    for article_tag in articles_tags:
        company_name = article_tag.find("div", class_="vacancy-serp-item__meta-info-company").text
        try:
            salary = article_tag.find("span", class_="bloko-header-section-3").text
        except AttributeError:
            salary = 'З/П не указана'
        h3_tag = article_tag.find("h3")
        a_tag = h3_tag.find("a")
        link = a_tag['href']

        article_html = requests.get(link, headers=get_headers()).text
        article_soup = BeautifulSoup(article_html, 'lxml')
        company_tag = article_soup.find("div", class_="vacancy-company-redesigned").text
        branded_article_text = article_soup.find("div", class_="vacancy-branded-user-content")
        if not branded_article_text:
            regular_article_text = article_soup.find("div", class_="g-user-content").text
            if re.findall('(Django+.*Flask+)|(Flask+.*Django+)', regular_article_text, flags=re.MULTILINE):
                city = re.findall("Москва|Санкт-Петербург", company_tag, flags=re.MULTILINE)[0]
                parsed_data.append(
                    {
                        "link": link,
                        "salary": salary,
                        "company_name": company_name,
                        "city": city
                    }
                )

        else:
            branded_article_text = article_soup.find("div", class_="vacancy-branded-user-content").text
            if re.findall('(Django+.*Flask+)|(Flask+.*Django+)', branded_article_text, flags=re.MULTILINE):
                city = re.findall("Москва|Санкт-Петербург", company_tag, flags=re.MULTILINE)[0]
                parsed_data.append(
                    {
                        "link": link,
                        "salary": salary,
                        "company_name": company_name,
                        "city": city
                    }
                )
    for data in parsed_data:
        data['salary'] = data['salary'].replace('\u202f', '')
        data['company_name'] = data['company_name'].replace('\xa0', ' ')
    return parsed_data


def write_json():
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(find_companies(), f, ensure_ascii=False)


if __name__ == '__main__':
    write_json()




