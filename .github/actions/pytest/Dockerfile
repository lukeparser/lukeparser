FROM python:slim

RUN apt-get update && \
    apt-get install -y bison flex

# install luke requirements
RUN pip install pybison tqdm six watchdog pytest

WORKDIR /github/workspace/tests

ENTRYPOINT ["pytest -v tests"]
