FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY Arquitectura/ /tmp/Arquitectura
RUN pip install /tmp/Arquitectura

COPY run.py /usr/src/app/run.py

CMD [ "python", "./run.py" ]