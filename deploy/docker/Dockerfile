FROM python:3.7-slim-buster
LABEL maintainer="Lambdaclass <jamoroso@lambdaclass.com>"

ARG USER="scraper"

ENV SCRAPER_HOME "/home/${USER}"
ENV LANG en_US.utf8

# Disable pip & pipenv cache to trim down image
ENV PIP_NO_CACHE_DIR true

RUN set -eux; \
	groupadd -r ${USER} --gid=999; \
	useradd -r -g ${USER} --uid=999 --home-dir=${SCRAPER_HOME} --shell=/bin/bash ${USER}; \
	mkdir -p ${SCRAPER_HOME}; \
	chown -R ${USER}:${USER} ${SCRAPER_HOME}

RUN pip3 install pipenv
RUN apt-get update && apt-get install -y make

USER ${USER}

COPY deploy/docker/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["make", "help"]

COPY . ${SCRAPER_HOME}
WORKDIR ${SCRAPER_HOME}

RUN pipenv --three && pipenv install --deploy
