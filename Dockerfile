FROM python:3.11.5-alpine

WORKDIR /app

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install

COPY src src
COPY docker-entrypoint.sh .
COPY schema.sql .
RUN chmod +x docker-entrypoint.sh


EXPOSE 5000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src", "src.app:app" ]
