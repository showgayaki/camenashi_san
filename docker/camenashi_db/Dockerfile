FROM mariadb:10.5.22 AS builder

RUN apt-get update -y && apt-get upgrade -y \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
locales \
&& localedef -f UTF-8 -i ja_JP ja_JP.UTF-8


FROM mariadb:10.5.22 AS prod

COPY --from=builder /usr/local/bin /usr/local/bin

ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TERM=xterm
ENV TZ=JST-9

# ARG DB_PORT
# RUN sed -i "s/\# port\s*=\s*3306/port = $DB_PORT/" /etc/mysql/my.cnf
COPY my.cnf /etc/mysql/conf.d/
COPY init.sql /docker-entrypoint-initdb.d/
