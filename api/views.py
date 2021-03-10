from flask import Blueprint, jsonify, request
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import pandas as pd
from . import db
from .models import Movie

main = Blueprint('main', __name__)

def scrap_detik():
    # detik
    url = "https://www.detik.com/search/searchall?query=perompakan"
    uClient = uReq(url)
    pageHtml = uClient.read()
    uClient.close()

    pageSoup = soup(pageHtml, "html.parser")

    containers = pageSoup.findAll("article")

    # add to array of news
    arrNews = []
    news = {
        "link" : "",
        "title" : ""
    }

    for container in containers :
        # tribun
        # newsLink = container.h3.a["href"]
        # newsTitle = container.h3.a.text.strip()

        # detik
        newsLink = container.a["href"]

        titleContainer = container.findAll("span", {"class":"box_text"})
        newsTitle = titleContainer[0].h2.text

        news = {
            "link" : newsLink,
            "title" : newsTitle
        }

        arrNews.append(news)

    # each news
    pageUrl = arrNews[0]['link']
    uClient = uReq(pageUrl)
    pageHtml = uClient.read()
    uClient.close()

    pageSoup = soup(pageHtml, "html.parser")

    container = pageSoup.findAll("article", {"class":"detail"})

    arrFullNews = []
    for news in arrNews :
        #detik
        pageUrl = news['link']
        uClient = uReq(pageUrl)
        pageHtml = uClient.read()
        uClient.close()

        pageSoup = soup(pageHtml, "html.parser")

        container = pageSoup.findAll("article", {"class":"detail"})

        # retrieve title, date, and author
        if(len(container) > 0) :
            title = container[0].div.h1.text.strip()
            

            authorContainer = container[0].findAll("div", {"class":"detail__author"})
            author = authorContainer[0].text

            dateContainer = container[0].findAll("div", {"class":"detail__date"})
            date = dateContainer[0].text

            fullContent = ""
            # retrieve content
            contentContainer = container[0].findAll("div", {"class":"detail__body-text"})
            contentText = contentContainer[0].findAll("p")

            for content in contentText :
                fullContent = fullContent + " " + content.text

            fullContent = fullContent.strip()

            news = {
                "link" : pageUrl,
                "title" : title,
                "author" : author,
                "date" : date,
                "content" : fullContent
            }

            arrFullNews.append(news)

    return arrFullNews
    # df = pd.DataFrame (arrFullNews, columns = ['link','title','author','date','content'])

    # df.to_csv('scrapYoutube-detik.csv', index=False)

@main.route('/add_movie', methods=['POST'])
def add_movie():
    movie_data = request.get_json()

    new_movie = Movie(title=movie_data['title'], rating=movie_data['rating'])

    db.session.add(new_movie)
    db.session.commit()

    return 'Done', 201

@main.route('/movies')
def movies():
    movie_list = Movie.query.all()
    movies = []

    for movie in movie_list:
        movies.append({'title' : movie.title, 'rating' : movie.rating})

    return jsonify({'movies' : movies})

@main.route('/news')
def news():
    news = []
    news = scrap_detik()

    return jsonify({'news' : news})