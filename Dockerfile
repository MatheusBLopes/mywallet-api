FROM python:3.10.4

ENV PYTHONBUFFERED=1
ENV LANG=C.UTF-8

RUN pip install poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    htop \
    tzdata \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install

ADD . /app/

RUN python mywallet-api/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn_config.py", "mywallet_api.wsgi:application"]
