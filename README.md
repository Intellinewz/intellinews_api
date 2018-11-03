# Intellinewz API

News feed API providing analysis on each articles' sentiment tones, reading level scores, total number of words, news source veracity/political leaning, and more!

----
## AWS Deployment EC2 Instance:
[http://ec2-18-223-109-140.us-east-2.compute.amazonaws.com/](http://ec2-18-223-109-140.us-east-2.compute.amazonaws.com/)

## Github Repository
[https://github.com/PythonMidterm/news_api](https://github.com/PythonMidterm/news_api)

----
## Table of Contents
* [Overview](#overview)
* [Technologies](#technologies)
* [Getting Started](#start)
* [Contributors](#participants)
* [Routes](#routes)
* [Wireframe](#wireframe)
* [Change Log](#change-log)
----
<a id="overview"></a>
## Overview:
The media we consume has significant effects on our mood, thoughts, and understanding of the world. The problem is that news outlets are incentivized not necessarily to inform, but to get users to subscribe, to tune in, or to click a link. In this light, headlines/content too often sensational, anecdotal, and appeal to emotion and not to our sense of reason. 

Our vision is to develop a news feed that provides rich data, analysis, and visualization of each article and news source by leveraging current open source NLP and other social science tools, so that users can get the most out of the news.

----
<a id="technologies"></a>
## Technologies employed:
- **API:** Pyramid Rest Framework (Pylons) and SqlAlchemy.
- **Primary 3rd party text analysis tools:** News API, Goose Text Extractor, IBM Watson Tone Analyzer, Textstat
- **Data Viz:** NumPy, Pandas, Matplotlib, Bokeh

----
<a id="start"></a>
## Getting Started:
- Clone the repository from github using the command "git clone [repository link]" in your CLI.
- Use "pipenv shell" in your command line to set up your virtual environment.
- Use "pipenv install" to install all of the necessary dependencies.
- Reference the README.txt for setting up the database in local dev.
- Use "pserve development.ini --reload" to start your server
- Hit API routes using Postman (or similar tool).
- React-based front-end is in development!
----
<a id="participants"></a>
## Particapants:
- Ben Hurst
- Justin Morris
- Madeline Peters
- Roman Kireev
- Luther Mckeiver
----
<a id="routes"></a>
## Routes (currently in flux, needs to be updated):
**Home:** `/`
* GET: Splash page with login prompt.

**Preferences:** `api/v1/preferences`
* GET: Review preferences in the database.
* POST: Change existing preferences. If no preferences given, default provided.
~~~
preference_order = {
        'preference_order': 'test@example.com',
    }
response.status_code == 201
~~~
* OTHER METHODS:
~~~~
response.status_code == 4**
~~~~

**Feed:** `api/v1/feed`
* GET: See your feed organized based on user preferences. If no user preferences, default preferences used.
* OTHER METHODS:
~~~~
response.status_code == 4**
~~~~
**Visuals:** `api/v1/visuals`
* GET: See visual representations of the data in our article archives.

**Authorization:**
* `api/v1/auth/{auth}`
* `api/v1/register`
* `api/v1/login`
* POST with successful auth:

~~~~
account = {
        'email': 'test@example.com',
        'password': 'hello',
    }
   response.json['token']
   response.status_code == 201
   ~~~~

* POST with unsuccessful auth (no token returned):
~~~~
account = {
        'email': 'test_two@example.com',
    }
    response.status_code == 400
~~~~

----

<a id="wireframe"></a>
## Initial concept wireframe:
![Wireframe ](/news_api/assets/wireframe.png)

----
<a id="change-log"></a>
## Change Log:

