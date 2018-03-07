FROM docker.io/python:3.6-slim

# ADD https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64 /usr/local/bin/dumb-init
# RUN chmod +x /usr/local/bin/dumb-init
COPY docker/dist/dumb-init_1.2.1_amd64 /usr/local/bin/dumb-init

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]

# Install dependencies
COPY Pipfile /tmp
COPY Pipfile.lock /tmp
RUN cd /tmp && \
    pip install -U pip && \
    pip install pipenv && \
    pipenv install --deploy --system && \
    rm -rf /tmp/Pipfile* /root/.cache
