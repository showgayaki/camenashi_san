FROM python:3.12-slim-bookworm

RUN apt-get update -y && apt-get upgrade -y \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
locales mariadb-client \
# required mariadb
gcc libmariadb-dev \
# required discord.py
libffi-dev libnacl-dev python3-dev \
&& localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
&& rm -rf /var/lib/apt/lists/* && apt-get clean && apt-get autoclean && apt-get autoremove \
&& pip install --upgrade pip setuptools

ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TERM=xterm
ENV TZ=JST-9

WORKDIR /app
COPY alembic.ini alembic.ini
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY bot/ bot/
ENTRYPOINT ["python", "bot/bot.py"]
