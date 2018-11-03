news_api
==========

Getting Started
---------------

- Change directory into your newly created project.

    cd news_api

- Enter the virtual environment.

    pipenv shell

- Install pip modules.

    pipenv install

- Install the project in editable mode with its testing requirements.

    pipenv install -e ".[testing]"

- Configure the database.

    initialize_news_api_db development.ini

- Run database migrations.

    alembic revision --autogenerate -m "{insert comment indicative of model changes}"
    alembic upgrade head

- Run your project's tests.

    pytest

- Run your project.

    pserve development.ini --reload
