FROM python:alpine3.7

RUN addgroup -g 1000 -S uwsgi && \
    adduser -u 1000 -S uwsgi -G uwsgi
RUN mkdir /src
WORKDIR /src
COPY Pipfile.lock /src/
COPY Pipfile /src/
RUN mkdir -p /var/cache/apk \
    && ln -s /var/cache/apk /etc/apk/cache
RUN apk update \
    && apk add --no-cache -u build-base linux-headers libffi-dev libressl-dev \
    && pip install --upgrade pip && pip install pipenv
COPY . /src
RUN pipenv install --system --ignore-pipfile
RUN pipenv install --system --dev
RUN apk cache clean
EXPOSE 5000
ENTRYPOINT ["/src/run.sh"]
