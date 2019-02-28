FROM python:3.7.2-alpine3.9

WORKDIR /server

RUN pip install Flask

COPY . /server

ENTRYPOINT [ "python" ]

CMD [ "auth_server.py" ]