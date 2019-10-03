FROM python:slim

RUN apt-get update && \
    apt-get install -y bison flex

# install luke requirements
RUN pip install pybison tqdm six watchdog

COPY entrypoint.sh /entrypoint.sh
WORKDIR /github/workspace

ENTRYPOINT ["/entrypoint.sh"]
