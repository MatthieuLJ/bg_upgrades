FROM python:3.10-alpine

# Install Imagemagick package
# gcc and more are required to build the uswgi wheel
RUN apk add imagemagick imagemagick-dev imagemagick-pdf gcc python3-dev build-base linux-headers pcre-dev curl

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /

RUN pip install -r requirements.txt

RUN addgroup --system app && adduser --system -s /bin/sh app

COPY django_app/ /app

COPY uwsgi/uwsgi.ini /app/
COPY uwsgi/start_uwsgi.sh /app/

WORKDIR /app/

RUN chmod +x start_uwsgi.sh