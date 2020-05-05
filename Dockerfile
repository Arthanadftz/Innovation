FROM python:3.7-alpine

ENV DEBIAN_FRONTEND noninteractive

COPY ./ci /opt/innovation/ci

RUN apk update &&\
    cat /opt/innovation/ci/apt-requirements.txt | xargs apk add
RUN python3 -m pip install -r /opt/innovation/ci/py-requirements.txt

COPY . /opt/innovation/
WORKDIR /opt/innovation/
RUN chmod +x /opt/innovation/docker-entrypoint.sh

VOLUME /opt/innovation/static/
EXPOSE 8000
ENTRYPOINT ["/opt/innovation/docker-entrypoint.sh"]

