FROM python:3.11.5-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src src
COPY docker-entrypoint.sh .
COPY schema.sql .
RUN chmod +x docker-entrypoint.sh


EXPOSE 5000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "./src", "src.app:app" ]
