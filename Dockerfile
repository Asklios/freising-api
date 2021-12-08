FROM python:3.9-slim-buster
RUN mkdir /app
WORKDIR /app

RUN python -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/python -m pip install --upgrade pip
RUN /opt/venv/bin/pip install -r requirements.txt

COPY . .

CMD ["/opt/venv/bin/python", "main.py"]