FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y bison flex

# install luke requirements
RUN pip install pybison tqdm six watchdog cython

COPY entrypoint.sh /entrypoint.sh
WORKDIR /github/workspace

ENTRYPOINT ["/entrypoint.sh"]
