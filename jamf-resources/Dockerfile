FROM python:3.8-slim-buster
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY perfmon /perfmon
RUN mkdir /logs
WORKDIR /perfmon
ENTRYPOINT [ "python3", "main.py" ]

