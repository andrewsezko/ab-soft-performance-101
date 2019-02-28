FROM python:3.7.2-alpine3.9

WORKDIR /server

RUN pip install Flask requests

COPY . /server

ENTRYPOINT [ "python" ]

CMD [ "product_server.py" ]