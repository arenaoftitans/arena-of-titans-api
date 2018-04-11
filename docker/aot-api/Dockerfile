FROM registry.gitlab.com/arenaoftitans/arena-of-titans-api/dev/aot-api:latest AS pythondev

COPY . aot /opt/aot-api/
RUN cd /opt/aot-api/ && \
    rm -rf dist && \
    ./setup.py sdist && \
    mv dist/*.tar.gz dist/aot-api.tar.gz

FROM registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:latest

# Install aot
COPY --from=pythondev /opt/aot-api/dist/aot-api.tar.gz /tmp/aot-api.tar.gz
RUN pip install /tmp/aot-api.tar.gz && \
    rm -rf /tmp/aot-api.tar.gz /root/.cache

# Create user with which to run the API.
RUN useradd --system aot
USER aot

CMD [ "/usr/local/bin/aot-api" ]
