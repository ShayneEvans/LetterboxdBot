import pytest
import html
from scraper_functions import get_movie_description, get_search_term_urls, get_cdata, get_movie_poster_url, get_movie_director, get_movie_title, get_rating_count, get_rating_value, get_release_year, get_varData_script, get_runtime, format_movie_runtime
from bs4 import BeautifulSoup
import requests
import json
import re

with open('valid_page_source.txt', 'r', encoding='utf-8') as file:
    valid_movie_html = file.read()

with open('invalid_page_source.txt', 'r', encoding='utf-8') as file:
    invalid_movie_html = file.read()

#Instead of scraping I decided to copy the page source of the webpages that are used on Letterboxd, one with valid fields for everything and one of a movie that is not yet released.
valid_movie_html_soup = BeautifulSoup(valid_movie_html, 'html.parser')
invalid_movie_html_soup = BeautifulSoup(invalid_movie_html, 'html.parser')

valid_movie_cdata = get_cdata(valid_movie_html_soup)
cleaned_valid_cdata = re.sub(r'\/\*.*?\*\/', '', valid_movie_cdata, flags=re.DOTALL).strip()
valid_json_data = json.loads(cleaned_valid_cdata)

invalid_movie_cdata = get_cdata(invalid_movie_html_soup)
cleaned_invalid_data = re.sub(r'\/\*.*?\*\/', '', invalid_movie_cdata, flags=re.DOTALL).strip()
invalid_json_data = json.loads(cleaned_invalid_data)

def test_get_movie_description_with_valid_doc():
    description = get_movie_description(valid_movie_html_soup)
    assert description == html.unescape("It ain&#039;t easy bein&#039; green -- especially if you&#039;re a likable (albeit smelly) ogre named Shrek. On a mission to retrieve a gorgeous princess from the clutches of a fire-breathing dragon, Shrek teams up with an unlikely compatriot -- a wisecracking donkey.")

def test_get_movie_description_with_invalid_doc():
    description = get_movie_description(invalid_movie_html_soup)
    assert description == "N/A"

#get search term urls testing
def test_get_search_term_urls_valid_title():
    search_term = "Shrek"
    result = get_search_term_urls(search_term)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0

def test_get_search_term_urls_invalid_title():
    search_term = "fsdlkfjdslfnasfdjs"
    result = get_search_term_urls(search_term)
    assert result is None

def test_get_cdata_from_html():
    assert get_cdata(valid_movie_html_soup).replace("\n","") == '/* <![CDATA[ */{"image":"https://a.ltrbxd.com/resized/film-poster/5/1/3/4/4/51344-shrek-0-230-0-345-crop.jpg?v=cd09df2c75","@type":"Movie","director":[{"@type":"Person","name":"Andrew Adamson","sameAs":"/director/andrew-adamson/"},{"@type":"Person","name":"Vicky Jenson","sameAs":"/director/vicky-jenson/"}],"dateModified":"2024-12-20","productionCompany":[{"@type":"Organization","name":"Pacific Data Images","sameAs":"/studio/pacific-data-images/"},{"@type":"Organization","name":"DreamWorks Animation","sameAs":"/studio/dreamworks-animation/"}],"releasedEvent":[{"@type":"PublicationEvent","startDate":"2001"}],"@context":"http://schema.org","url":"https://letterboxd.com/film/shrek/","actors":[{"@type":"Person","name":"Mike Myers","sameAs":"/actor/mike-myers/"},{"@type":"Person","name":"Eddie Murphy","sameAs":"/actor/eddie-murphy/"},{"@type":"Person","name":"Cameron Diaz","sameAs":"/actor/cameron-diaz/"},{"@type":"Person","name":"John Lithgow","sameAs":"/actor/john-lithgow/"},{"@type":"Person","name":"Vincent Cassel","sameAs":"/actor/vincent-cassel/"},{"@type":"Person","name":"Peter Dennis","sameAs":"/actor/peter-dennis/"},{"@type":"Person","name":"Clive Pearse","sameAs":"/actor/clive-pearse/"},{"@type":"Person","name":"Jim Cummings","sameAs":"/actor/jim-cummings/"},{"@type":"Person","name":"Bobby Block","sameAs":"/actor/bobby-block/"},{"@type":"Person","name":"Chris Miller","sameAs":"/actor/chris-miller-1/"},{"@type":"Person","name":"Cody Cameron","sameAs":"/actor/cody-cameron/"},{"@type":"Person","name":"Kathleen Freeman","sameAs":"/actor/kathleen-freeman/"},{"@type":"Person","name":"Michael Galasso","sameAs":"/actor/michael-galasso-1/"},{"@type":"Person","name":"Christopher Knights","sameAs":"/actor/christopher-knights/"},{"@type":"Person","name":"Simon J. Smith","sameAs":"/actor/simon-j-smith/"},{"@type":"Person","name":"Conrad Vernon","sameAs":"/actor/conrad-vernon/"},{"@type":"Person","name":"Jacquie Barnbrook","sameAs":"/actor/jacquie-barnbrook/"},{"@type":"Person","name":"Guillaume Aretos","sameAs":"/actor/guillaume-aretos/"},{"@type":"Person","name":"John Bisom","sameAs":"/actor/john-bisom/"},{"@type":"Person","name":"Matthew Gonder","sameAs":"/actor/matthew-gonder/"},{"@type":"Person","name":"Calvin Remsberg","sameAs":"/actor/calvin-remsberg/"},{"@type":"Person","name":"Jean-Paul Vignon","sameAs":"/actor/jean-paul-vignon/"},{"@type":"Person","name":"Val Bettin","sameAs":"/actor/val-bettin/"},{"@type":"Person","name":"Andrew Adamson","sameAs":"/actor/andrew-adamson/"},{"@type":"Person","name":"Gary A. Hecker","sameAs":"/actor/gary-a-hecker/"}],"dateCreated":"2011-06-22","name":"Shrek","genre":["Adventure","Fantasy","Family","Animation","Comedy"],"@id":"https://letterboxd.com/film/shrek/","countryOfOrigin":[{"@type":"Country","name":"USA"}],"aggregateRating":{"bestRating":5,"reviewCount":112367,"@type":"aggregateRating","ratingValue":4.1,"description":"The Letterboxd rating is a weighted average score for a movie based on all ratings cast to date by our members.","ratingCount":1524195,"worstRating":0}}/* ]]> */'

#Testing if able to extract poster URL from a CDATA that contains a poster image field
def test_get_movie_poster_url_valid_poster():
    assert get_movie_poster_url(valid_json_data) == "https://a.ltrbxd.com/resized/film-poster/5/1/3/4/4/51344-shrek-0-230-0-345-crop.jpg?v=cd09df2c75" 

#Testing that None is returned when poster image field is not present
def test_get_movie_poster_url_no_poster():
    assert get_movie_poster_url(invalid_json_data) == None

#Testing if able to extract director name from CDATA that contains a director field
def test_get_movie_director_valid_director():
    assert get_movie_director(valid_json_data) == "Andrew Adamson"

#Testing that N/A is returned when movie has no director field
def test_get_movie_director_invalid_director():
    assert get_movie_director(invalid_json_data) == "N/A"

#Testing if able to extract rating value from CDATA that contains a avg rating field
def test_get_valid_rating_value():
    assert get_rating_value(valid_json_data) == 4.1

#Testing that not enough ratings message is returned when movie does not have enough ratings to have an average rating
def test_get_invalid_rating_value():
    assert get_rating_value(invalid_json_data) == "Not Enough Ratings to get Average Rating"

#Testing if able to extract rating count from CDATA that contains a ratingCount field
def test_get_valid_review_count():
    assert get_rating_count(valid_json_data) == f'{int("1524195"):,}'

#Testing that N/A is returned when there is no ratingCount field for a movie
def test_get_invalid_review_count():
    assert get_rating_count(invalid_json_data) == 'N/A'

#Testing if able to extract movie release year from CDATA that contains startDate field
def test_get_valid_release_year():
    assert get_release_year(valid_json_data) == "2001"

#Testing that N/A is returned when there is no startDate field for a movie
def test_get_valid_release_year():
    assert get_release_year(invalid_json_data) == "N/A"

#Testing if formatting the runtime return appropriately
def test_format_movie_runtime():
    assert format_movie_runtime(60) == "1h"
    assert format_movie_runtime(125) == "2h 5m"
    assert format_movie_runtime(2) == "2m"

#Testing if able to extract movie runtime field from vardata
def test_get_runtime():
    assert get_runtime(valid_movie_html_soup) == "1h 30m"

#Testing is N/A if returned if movie runtime field is not present in vardata
def test_get_invalid_runtime():
    assert get_runtime(invalid_movie_html_soup) == "N/A"

#Testing if able to extract movie title field from vardata
def test_get_valid_movie_title():
    assert get_movie_title(valid_json_data) == "Shrek"

#Testing if N/A is returned if movie title field is not present in cdata
def test_get_invalid_movie_title():
    assert get_movie_title(invalid_json_data) == "N/A"