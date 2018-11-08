from ..models.feed import Feed
from ..models.archives import Archives
from watson_developer_cloud import ToneAnalyzerV3
from goose3 import Goose
import goose3
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sys import platform
from .visuals import render_pie_charts
import os
import textstat
import json


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


def analyze_vocab(text):
    return {
        'num_words':
        textstat.lexicon_count(text),
        'flesch_reading_ease':
        textstat.flesch_reading_ease(text),
        'smog_index':
        textstat.smog_index(text),
        'flesch_kincaid_grade':
        textstat.flesch_kincaid_grade(text),
        'coleman_liau_index':
        textstat.coleman_liau_index(text),
        'automated_readability_index':
        textstat.automated_readability_index(text),
        'dale_chall_readability_score':
        textstat.dale_chall_readability_score(text),
        'difficult_words':
        textstat.difficult_words(text),
        'linsear_write_formula':
        textstat.linsear_write_formula(text),
        'gunning_fog':
        textstat.gunning_fog(text),
        'text_standard':
        textstat.text_standard(text, float_output=True)
    }


# TODO: This function is too long. Refactor further.

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
    session.query(Feed).delete()
    session.commit()

    api_response = get_news()

    parsed_article_list = []

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

        vocab_analysis = analyze_vocab(text)
        tone_analysis = analyze_text(text).get_result()

        num_analyzed_sentences = 0
        sentence_breakdown = {
            'Analytical': 0,
            'Tentative': 0,
            'Confident': 0,
            'Joy': 0,
            'Anger': 0,
            'Fear': 0,
            'Sadness': 0
        }
        if 'sentences_tone' in tone_analysis:
            for sentence in tone_analysis['sentences_tone']:
                if len(sentence['tones']):
                    num_analyzed_sentences += 1
                    dom_sentence_tone = sorted(
                        sentence['tones'],
                        key=lambda k: k['score'])[-1]['tone_name']
                    sentence_breakdown[dom_sentence_tone] += 1
            for key, val in sentence_breakdown.items():
                sentence_breakdown[key] = round(val / num_analyzed_sentences, 2)

        if len(tone_analysis['document_tone']['tones']):
            dom_tone = tone_analysis['document_tone']['tones'][-1]['tone_name']
            article = {
                'title': article['title'],
                'url': article['url'],
                'description': article['description'],
                'source': article['source'],
                'date_published': article['date_published'],
                'image': article['image'],
                'dom_tone': dom_tone,
                'num_words': vocab_analysis['num_words'],
                'sentence_breakdown': sentence_breakdown,
                'vocab_score': vocab_analysis['text_standard'],
                }
            analyzed_articles.append(article)

            try:
                article_to_insert = Feed(
                    title=article['title'],
                    description=article['description'],
                    source=article['source'],
                    date_published=article['date_published'],
                    url=article['url'],
                    dom_tone=article['dom_tone'],
                    image=article['image'],
                    num_words=article['num_words'],
                    sentence_breakdown=article['sentence_breakdown'],
                    vocab_score=article['vocab_score'],
                )

                article_to_insert_archive = Archives(
                    title=article['title'],
                    description=article['description'],
                    source=article['source'],
                    date_published=article['date_published'],
                    url=article['url'],
                    dom_tone=article['dom_tone'],
                    image=article['image'],
                    num_words=article['num_words'],
                    sentence_breakdown=article['sentence_breakdown'],
                    vocab_score=article['vocab_score'],
                )

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
                    # Here create pie chart for each source


                    render_pie_charts(session)
                    session.commit()
                    continue

            except TypeError:
                continue

        session.commit()
