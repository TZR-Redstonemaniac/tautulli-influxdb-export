FROM python:3

RUN mkdir /work
COPY . /work
WORKDIR /work

RUN pip install -r requirements.txt
CMD python tautulli_influxdb_export.py