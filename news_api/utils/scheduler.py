from ..models.feed import Feed
from ..models.archives import Archives
from watson_developer_cloud import ToneAnalyzerV3
from goose3 import Goose
import goose3
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sys import platform
import os


def connect_to_db(db_path):
    """This function creates an engine and a session.
    """
    my_engine = create_engine(db_path)

    # create a configured "Session" class
    Session = sessionmaker(bind=my_engine)

    # create a Session
    return Session()


def get_news():
    """Function that fetches 20 current headlines from the News API
    """

    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey={}'.format(os.environ.get('NEWS_API_KEY'))
    response = requests.get(url)

    return response.json()['articles']


def extract_text(url):
    """Function to extract text from article
    """
    g = Goose()

    try:
        article = g.extract(url)
    except goose3.network.NetworkError:
        return False

    return article.cleaned_text


def analyze_text(text):
    # tone_analyzer = ToneAnalyzerV3(
    #         version='2017-09-21',
    #         username='637f0158-041b-45af-99c6-1035adfcb148',
    #         password='fooszZRwri2t')

    tone_analyzer = ToneAnalyzerV3(
        version='2017-09-21',
        iam_apikey=os.environ.get('WATSON_KEY'),
        url='https://gateway.watsonplatform.net/tone-analyzer/api'
    )

    return tone_analyzer.tone(
            {'text': text},
            'application/json')


def job():
    """Job to be scheduled for 3-step News Fetch/Extraction/Analyze.
    We can trigger at a specified interval (24-hour for demo purposes.
    1-hr or less in true production)
    """

    if platform == "linux" or platform == "linux2":
        db_path = os.environ.get('RDS_PATH')
    elif platform == "darwin":
        db_path = 'postgres://localhost:5432/news_api'


    session = connect_to_db(db_path)

    # TODO: Archive data before deleting. In a for loop, retrieve each row from the feed table, then post to the archive table.
    session.query(Feed).delete()
    session.commit()

    api_response = get_news()

    parsed_article_list = []

    # TODO: Expand parsed_article below to include description, source, data published, etc.
    for obj in api_response:
        parsed_article = {
            'title': obj['title'],
            'url': obj['url'],
            'description': obj['description'],
            'source': obj['source']['name'],
            'date_published': obj['publishedAt'],
            'image': obj['urlToImage'],
            }
        parsed_article_list.append(parsed_article)

    analyzed_articles = []

    for article in parsed_article_list:
        url = article['url']

        text = extract_text(url)
        if not text:
            continue

        tone_analysis = analyze_text(text).get_result()

        if len(tone_analysis['document_tone']['tones']):
            dom_tone = tone_analysis['document_tone']['tones'][-1]['tone_name']
            article = {
                'title': article['title'],
                'url': article['url'],
                'description': article['description'],
                'source': article['source'],
                'date_published': article['date_published'],
                'image': article['image'],
                'dom_tone': dom_tone
                }
            analyzed_articles.append(article)

            try:
                article_to_insert = Feed(title=article['title'], description=article['description'], source=article['source'], date_published=article['date_published'], url=article['url'], dom_tone=article['dom_tone'], image=article['image'])
                article_to_insert_archive = Archives(title=article['title'], description=article['description'], source=article['source'], date_published=article['date_published'], url=article['url'], dom_tone=article['dom_tone'], image=article['image'])
                article_exists = session.query(
                    session.query(Feed).filter_by(title=article['title']).exists()).scalar()
                if not article_exists:
                    session.add(article_to_insert)
                else:
                    session.commit()
                    continue


                exists = session.query(
                    session.query(Archives).filter_by(title=article['title']).exists()).scalar()
                if not exists:
                    session.add(article_to_insert_archive)
                else:
                    session.commit()
                    continue

            except TypeError:
                continue

        session.commit()
