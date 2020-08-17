FROM python:slim

COPY healthcheck.py entrypoint.sh README.md MANIFEST.ini setup.py /opt/recipes/
COPY recipes /opt/recipes/recipes
COPY config /config

WORKDIR /opt/recipes

RUN apt-get update && apt-get install --no-install-recommends -y tini \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove -y \
    && rm -rf \
        /tmp/* \
        /var/lib/apt/lists/* \
        /var/tmp/*

RUN python3 setup.py install \
    && useradd -r recipes \
    && chown -R recipes:recipes /opt/recipes /config

VOLUME /config

EXPOSE 8288

USER recipes

HEALTHCHECK --interval=5m --timeout=3s \
    CMD ["python3", "healthcheck.py"]

ENTRYPOINT ["/usr/bin/tini", "--", "/opt/recipes/entrypoint.sh"]
