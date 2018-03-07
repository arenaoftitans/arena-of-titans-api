FROM registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:latest

RUN apt-get -y update && \
        apt-get -y install make && \
        apt-get -y clean

COPY Pipfile /tmp
COPY Pipfile.lock /tmp

# Install dev dependencies
RUN cd /tmp && \
    pipenv install --dev --deploy --system && \
    rm -rf /tmp/Pipfile* /root/.cache
