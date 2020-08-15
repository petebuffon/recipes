FROM python:slim

COPY . /recipes

WORKDIR /recipes

RUN python3 setup.py install \
    && useradd -r -u 333 recipes \
    && chown -R recipes:recipes /recipes

WORKDIR /recipes/recipes

VOLUME /recipes

EXPOSE 8288

USER recipes

CMD ["gunicorn", "-b", ":8288", "--chdir", "/recipes/recipes", "recipes:app"]
