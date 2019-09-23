# dev mode:
# FROM baptest
# ADD bapylon_server.py /home

# release
FROM python:alpine

RUN apk update
RUN apk add bison flex curl git alpine-sdk

ADD . /home
WORKDIR /home
RUN pip install -r requirements.txt

CMD ["python3", "luke_server.py"]
