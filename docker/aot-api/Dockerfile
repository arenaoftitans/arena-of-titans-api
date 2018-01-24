FROM docker.io/python:3.6-slim

RUN apt-get -y update && \
        apt-get -y install make && \
        apt-get -y install nano vim && \
        apt-get -y install wget && \
        apt-get -y clean

RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64
RUN chmod +x /usr/local/bin/dumb-init
RUN apt-get -y autoremove wget

ADD Pipfile /tmp
ADD Pipfile.lock /tmp
ADD Makefile /tmp

RUN cd /tmp && make deps
RUN rm /tmp/Pipfile* /tmp/Makefile

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
