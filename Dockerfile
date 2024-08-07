FROM python:3.10-slim-buster
LABEL authors="enard"

WORKDIR /app
VOLUME /app/videos
EXPOSE 8000

COPY . .

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app_ws:app", ""]
