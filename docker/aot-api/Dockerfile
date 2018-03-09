FROM registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:latest

# Install aot
COPY dist/*.tar.gz /tmp/aot-api.tar.gz
RUN pip install /tmp/aot-api.tar.gz && \
    rm -rf /tmp/aot-api.tar.gz /root/.cache

# Create user with which to run the API.
RUN useradd --system aot
USER aot

CMD [ "/usr/local/bin/aot-api" ]
