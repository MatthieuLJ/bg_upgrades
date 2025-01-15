FROM python:3.10-alpine

# Install Imagemagick package
# gcc and more are required to build the uswgi wheel
RUN apk add imagemagick imagemagick-dev gcc python3-dev build-base linux-headers pcre-dev curl

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /

RUN pip install -r requirements.txt

WORKDIR /app

COPY django_app/ .

RUN python3 ./manage.py migrate

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

