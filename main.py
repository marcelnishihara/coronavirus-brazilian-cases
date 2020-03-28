import requests, re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

globals = {
    "url" : "https://www.xml-sitemaps.com/download/www.saude.gov.br-eeed47d82/sitemap.xml?view=1",
    "dictionary_of_stats" : {}
}

colors = {
    "err" : "\033[91m",
    "end" : "\033[m",
    "success" : "\033[92m",
    "warning" : "\033[93m"
}


def main(request):
    xml_content = get_xml()
    articles_urls = get_coronvirus_stats_urls(xml_content)

    for article_index, article_url in enumerate(articles_urls):
        accessing_url_message = f"Trying to access {article_url}"
        pretty_print(accessing_url_message, True)

        stats, date = get_stats_and_date(articles_urls[article_index])
        current_dictionary_of_stats = compose_dictionary_of_stats(stats)
        is_filled = bool(current_dictionary_of_stats)

        if is_filled:
            globals["dictionary_of_stats"][date] = current_dictionary_of_stats

    return globals["dictionary_of_stats"]


def get_xml():
    sitemap_url = globals["url"]
    request_url = requests.get(sitemap_url)
    status_code = request_url.status_code

    if status_code != 200:
        msg_err = f"Code: {status_code}.\nUnable to Access the URL: {sitemap_url}\nExiting Program."
        pretty_print(msg_err, False)
        exit()
    else :
        msg_success = f"Code: {status_code}.\nSitemap URL Accessed Successfully.\nSitemap URL: {sitemap_url}"
        pretty_print(msg_success, True)
        return request_url.content


def pretty_print(msg, status):
    if status == True:
        format_msg = f"{colors['success']}{msg}{colors['end']}"
    else :
        format_msg = f"{colors['err']}{msg}{colors['end']}"

    print(format_msg, end="\n\n")


def get_coronvirus_stats_urls(content):
    content_fromstring = ET.ElementTree(ET.fromstring(content))
    articles_urls = []

    for articles in content_fromstring.iter():
        value_of_text = articles.text
        is_corona_stats_news = re.search(r"[0-9]*-coronavirus-.*-mortes", value_of_text)

        if is_corona_stats_news:
            articles_urls.append(value_of_text)

    return articles_urls


def get_stats_and_date(site):
    article = requests.get(site)
    article_html = article.text

    regex_date = re.search(r"\"datePublished\"\:\ \"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})\"", article_html)
    date_published = regex_date.group(1)

    soup = BeautifulSoup(article_html, "html.parser")
    full_stats = []
    tds = []

    for tr in soup.find_all("tr") :
        current_td = tr.find_all("td")
        tds.append(current_td)

    for index_of_td in tds[2:]:
        temp_stats = []

        for i, items in enumerate(index_of_td):            
            trim_item = items.text.strip()
            trim_item_length = len(trim_item)
            brasil_total_of_cases = re.search(r"BRASIL", trim_item)

            if (trim_item_length < 10 or brasil_total_of_cases):
               temp_stats.append(trim_item)
        
        if len(temp_stats) != 0:
            full_stats.append(temp_stats)

    return full_stats, date_published


def compose_dictionary_of_stats(arr):
    current_dictionary_of_stats = {}

    for current_array in arr:
        is_state_stats = len(current_array) == 5

        if is_state_stats:
            state_form = current_array[1].strip()
            cases_form = int(current_array[2].replace(".", ""))
            deathes_form = int(current_array[3].replace(".", ""))
            deathes_per_cases_form = float("{0:.4f}".format((deathes_form/cases_form)*100))

            temp_uf_stats = {
                "state"             : state_form,
                "cases"             : cases_form,
                "deathes"           : deathes_form,
                "deathes_per_cases" : deathes_per_cases_form
            }

            uf_id = int(current_array[0])
            current_dictionary_of_stats[uf_id] = temp_uf_stats

    return current_dictionary_of_stats


if __name__ == "__main__":
    main()
