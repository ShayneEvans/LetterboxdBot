from bs4 import BeautifulSoup
import requests
import re
import json

def get_movie_description(doc):
    div = doc.find(class_="truncate")
    if div is not None:
        movie_description = div.find("p")
        return movie_description.text
    else:
        return "N/A"

def get_search_term_urls(search_term):
    url = "https://letterboxd.com/s/search/" + search_term + "/?"
    result = requests.get(url)
    search_html_doc = BeautifulSoup(result.text, "html.parser")
    search_results = search_html_doc.find(class_="results")


    if search_results is None:
        return None

    movie_list = search_results.find_all("li")

    #Obtaining all movies that appear on first page of letterboxd (max 20)
    movie_link_list = []
    for movie in movie_list:
        #Find the div with the data-film-slug attribute
        movie_div = movie.find('div', {'data-film-slug': True})
        if movie_div:
            movie_page_url = movie_div['data-film-slug']
            movie_link_list.append(f"https://letterboxd.com/film/{movie_page_url}")
            
    return movie_link_list

def get_cdata(doc):
    cdata = doc.find(text=re.compile("CDATA"))
    return str(cdata)

def get_movie_poster_url(json_cdata):
    try:
        if "image" in json_cdata:
            movie_poster_url = json_cdata["image"]
            if movie_poster_url is not None:
                return movie_poster_url
        else:
            return None
    except KeyError:
        return "N/A"

def get_movie_director(json_cdata):
    try:
        if "director" in json_cdata:
            movie_director = json_cdata["director"][0]["name"]
            if movie_director is not None:
                return movie_director
        else:
            return "N/A"
    except KeyError:
        return "N/A"

def get_rating_value(json_cdata):
    if "aggregateRating" in json_cdata:
        ratingValue = json_cdata["aggregateRating"]["ratingValue"]
        if ratingValue is not None:
            return ratingValue
    else:
        return "Not Enough Ratings to get Average Rating"

def get_rating_count(json_cdata):
    try:
        if "aggregateRating" in json_cdata:
            ratingCount = json_cdata["aggregateRating"]["ratingCount"]
            if ratingCount is not None:
                return f'{int(ratingCount):,}'
        else:
            return "N/A"
    except KeyError:
        return "N/A"

def get_release_year(json_cdata):
    try:
        if "releasedEvent" in json_cdata and len(json_cdata["releasedEvent"]) > 0:
            return json_cdata["releasedEvent"][0].get("startDate", "N/A")
        else:
            return "N/A"
    except KeyError:
        return "N/A"

def format_movie_runtime(movie_runtime_in_mins):
    if movie_runtime_in_mins == 60:
        return "1h"
    elif movie_runtime_in_mins >= 60:
        hours = movie_runtime_in_mins // 60
        minutes = movie_runtime_in_mins % 60
        return f'{hours}h {minutes}m'
    else:
        return f'{movie_runtime_in_mins}m'

def get_varData_script(doc):
    return doc.find_all("script")[4].string

def get_runtime(doc):
    movie_runtime_p = doc.find("p", class_="text-link text-footer")

    if movie_runtime_p:
        runtime_text = movie_runtime_p.get_text()
        match = re.search(r'(\d+)\s*mins', runtime_text)
        if match:
            return format_movie_runtime(int(match.group(1)))
    return "N/A"

def get_movie_title(json_cdata):
    try:
        if "name" in json_cdata:
            movie_title = json_cdata["name"]
            if movie_title is not None:
                return movie_title
        else:
            return "N/A"
    except KeyError:
        return "N/A"

def scrape_website(search_term_link):
        result = requests.get(search_term_link)
        doc = BeautifulSoup(result.text, "html.parser")
        cdata = get_cdata(doc)
        cleaned_cdata = re.sub(r'\/\*.*?\*\/', '', cdata, flags=re.DOTALL).strip()
        json_data = json.loads(cleaned_cdata)
        #Getting all stuffs
        movie_poster_url = get_movie_poster_url(json_data)
        movie_title =  get_movie_title(json_data)
        movie_director = get_movie_director(json_data)
        movie_release_year = get_release_year(json_data)
        movie_runtime = get_runtime(doc)
        movie_description = get_movie_description(doc)
        rating_value = get_rating_value(json_data)
        review_count = get_rating_count(json_data)

        return movie_poster_url, movie_title, movie_director, movie_release_year, movie_runtime, movie_description, rating_value, review_count
