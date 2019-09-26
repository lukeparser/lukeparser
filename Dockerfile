FROM python:slim

RUN pip install lukeparser
RUN luke --init

ENV hostname=0.0.0.0
ENV root_dir="/home"
CMD ["luke-server"]
