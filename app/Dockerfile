FROM python:3.11.9-alpine3.19 as build


RUN mkdir -p /app/logs \
    && addgroup app \
    && adduser -D -G app -h /app app \
    && chown -R app:app /app

WORKDIR /app

USER app

COPY --chown=app:app requirements.txt .

RUN python -m pip install --no-cache-dir -r ./requirements.txt

COPY --chown=app:app ./app.py ./app.py

ENTRYPOINT [ "python", "app.py" ]



