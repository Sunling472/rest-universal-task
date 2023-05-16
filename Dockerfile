FROM python:3.11.3-alpine

WORKDIR /usr/src/app/fast_template
ENV PYTHONPATH /usr/src/app/

RUN apk add --no-cache bash
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev && apk add libmagic

COPY . .

RUN pip install --use-deprecated=legacy-resolver --no-cache-dir \
    -r /usr/src/app/fast_template/requirements.txt
