FROM python:slim

RUN pip install lukeparser

ENV hostname=0.0.0.0
ENV root_dir="/home"
CMD ["luke", "--live"]
