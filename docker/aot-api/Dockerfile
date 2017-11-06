FROM docker.io/python:3.6-slim

RUN apt-get -y update && \
        apt-get -y install make && \
        apt-get -y install nano vim && \
        apt-get -y clean

ADD Pipfile /tmp
ADD Pipfile.lock /tmp
ADD Makefile /tmp

RUN cd /tmp && make deps
RUN rm /tmp/Pipfile* /tmp/Makefile
