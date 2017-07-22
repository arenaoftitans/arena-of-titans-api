FROM docker.io/python:3.6

ADD requires.txt /tmp
ADD tests_requires.txt /tmp
ADD Makefile /tmp

RUN apt-get -y update && \
        apt-get -y install nano vim && \
        apt-get -y clean

RUN cd /tmp && make deps
RUN rm /tmp/requires.txt /tmp/tests_requires.txt /tmp/Makefile
