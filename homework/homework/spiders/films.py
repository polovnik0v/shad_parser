from typing import Iterable
import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup
import requests

class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]
    
    def parse(self, response):
        film_links = response.css('li > a::attr(href)').getall()
        for film_link in film_links:
            yield response.follow(film_link, self.film_page_parse)
        

        next_page = response.xpath('//a[contains(@title, "Фильмы по алфавиту") and contains(text(), "Следующая страница")]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def film_page_parse(self, response):

        imdb_id = self.get_imdb_id(response.css('tr th.infobox-above::text').get())
        if imdb_id:
            imdb_rating = self.get_imdb_rating(imdb_id)
            imdb = imdb_rating
        else:
            imdb = 'N/A'

        film_details = {
            'title': response.css('tr th.infobox-above::text').get(),
            'genre': response.css('tr:contains("Жанр")  td.plainlist  span a::text').get(),
            'year': response.css('tr:contains("Год") td.plainlist span::text').get(),
            'country': response.css('tr:contains("Страна") td.plainlist a span::text').get(),
            'director': response.css('tr:contains("Режиссёр") span a::text').get(),
            'imbd': imdb
            }
        
        yield film_details  

    def get_imdb_id(self, film_title):

        tmdb_api_key = '3c71534f364b85ff006d9b1d64c05e3a'
        tmdb_search_url = f'https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={film_title}'

        response = requests.get(tmdb_search_url)
        data = response.json()

        if 'results' in data and data['results']:
            imdb_id = data['results'][0]['id']
            return imdb_id
        else:
            return None

    def get_imdb_rating(self, imdb_id):


        tmdb_api_key = '3c71534f364b85ff006d9b1d64c05e3a'
        tmdb_movie_url = f'https://api.themoviedb.org/3/movie/{imdb_id}?api_key={tmdb_api_key}'

        response = requests.get(tmdb_movie_url)
        data = response.json()

        if 'vote_average' in data:
            imdb_rating = data['vote_average']
            return imdb_rating
        else:
            return 'N/A'
