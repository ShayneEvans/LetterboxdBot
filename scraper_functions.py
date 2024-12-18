from bs4 import BeautifulSoup
import requests
import re

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

def get_movie_poster_url(cdata):
    find_movie_poster_url = re.search(r'{\"image\":\"(.*?)\",\"', cdata)
    if find_movie_poster_url is not None:
        return find_movie_poster_url.group(1)
    else:
        return None

def get_movie_director(cdata):
    find_movie_director = re.search(r'\"director\":\[{\"@type\":\"Person\",\"name\":\"(.*?)\",\"sameAs\"', cdata)
    if find_movie_director is not None:
        return find_movie_director.group(1)
    else:
        return "N/A"

def get_rating_value(cdata):
    find_ratingValue = re.search(r'\"ratingValue\":(.*?),\"description\":', cdata)
    if find_ratingValue is not None:
        return find_ratingValue.group(1)
    else:
        return "Not Enough Ratings to get Average Rating"

def get_review_count(cdata):
    find_ratingCount = re.search(r'members.\",\"ratingCount\":(.*?),\"worstRating\":', cdata)
    if find_ratingCount is not None:
        return f'{int(find_ratingCount.group(1)):,}'
    else:
        return "N/A"

def get_release_year(cdata):
    find_release_year = re.search(r'\"@type":\"PublicationEvent\",\"startDate\":\"(.*?)\"}', cdata)
    if find_release_year is not None:
        return find_release_year.group(1)
    else:
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

def get_movie_title(cdata):
    find_movie_title = re.search(r'"dateCreated":".*?","name":"(.*?)",.*?"genre":', cdata)
    if find_movie_title is not None:
        #Sometime's title erroneously has a \ in it, so replace it with nothing
        return find_movie_title.group(1).replace("\\", "")
    else:
        return "N/A"

def scrape_website(search_term_link):
        result = requests.get(search_term_link)
        doc = BeautifulSoup(result.text, "html.parser")
        cdata = get_cdata(doc)
        #varData has been obsoleted as of 12/18
        #varData_script_string = get_varData_script(doc)

        #Getting all stuffs
        movie_poster_url = get_movie_poster_url(cdata)
        movie_title =  get_movie_title(cdata)
        movie_director = get_movie_director(cdata)
        movie_release_year = get_release_year(cdata)
        movie_runtime = get_runtime(doc)
        movie_description = get_movie_description(doc)
        rating_value = get_rating_value(cdata)
        review_count = get_review_count(cdata)

        return movie_poster_url, movie_title, movie_director, movie_release_year, movie_runtime, movie_description, rating_value, review_count
