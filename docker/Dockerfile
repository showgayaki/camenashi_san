# 参考
# https://zenn.dev/niku/scraps/fd6e620a0d374b
FROM python:3.12-slim-bookworm AS base
ARG TARGETARCH

FROM base AS amd64
ENV ARCH x86_64

FROM base AS arm64
ENV ARCH aarch64


FROM python:3.12-slim-bookworm AS builder

COPY requirements.txt requirements.txt

RUN apt-get update -y && apt-get upgrade -y \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
locales \
# required mariadb
gcc libmariadb-dev \
# required discord.py
libffi-dev libnacl-dev python3-dev \
# required matplotlib(日本語対応フォント)
fonts-noto-cjk \
&& localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
&& pip install --upgrade pip setuptools && \
pip install --no-cache-dir --upgrade -r requirements.txt


FROM ${TARGETARCH} AS prod

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/lib/${ARCH}-linux-gnu/libmariadb.so.3 /usr/lib/${ARCH}-linux-gnu/libmariadb.so.3
COPY --from=builder /usr/share/fonts/ /usr/share/fonts/

ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TERM=xterm
ENV TZ=JST-9

WORKDIR /app
COPY alembic.ini alembic.ini
COPY alembic/ alembic/
COPY bot/ bot/

ENTRYPOINT ["python", "bot/bot.py"]
