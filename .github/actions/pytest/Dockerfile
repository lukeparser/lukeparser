FROM python:slim

RUN apt-get update && \
    apt-get install -y bison flex

# install luke requirements
RUN pip install pybison tqdm six watchdog pytest

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
WORKDIR /github/workspace/tests

ENTRYPOINT ["/entrypoint.sh"]
