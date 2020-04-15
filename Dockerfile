#Grab the latest alpine image
FROM alpine:latest

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk add --no-cache postgresql-libs musl-dev postgresql-dev
RUN apk --no-cache --update-cache add gcc gfortran python3 python3-dev py3-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip3 install cython
RUN pip3 install matplotlib==3.1.3
RUN pip3 install numpy==1.18.2

# Install python and pip
ADD requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip3 install -r /tmp/requirements.txt

# Add our code
ADD . /opt/webapp/
WORKDIR /opt/webapp

# Expose is NOT supported by Heroku
# EXPOSE 5000

RUN apk add bash

# Run the image as a non-root user
RUN adduser -D myuser
USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD gunicorn --bind 0.0.0.0:$PORT home.wsgi.dev
