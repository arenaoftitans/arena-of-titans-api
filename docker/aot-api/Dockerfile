FROM registry.gitlab.com/arenaoftitans/arena-of-titans-api/base/aot-api:latest

# Install aot
COPY . aot /opt/aot-api/

# Create user with which to run the API.
RUN useradd --system aot
USER aot
WORKDIR "/opt/aot-api"

CMD [ "python", "-m", "aot" ]
