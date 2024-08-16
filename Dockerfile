FROM python:3.10-slim-buster
LABEL authors="enard"

WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /app/videos
EXPOSE 8000

COPY . .

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app_ws:app", ""]
