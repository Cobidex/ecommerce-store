FROM python:3.9-slim-buster
WORKDIR /app
COPY ./requirements.txt /app
RUN apt-get update && apt-get -y install python3-dev default-libmysqlclient-dev build-essential pkg-config

RUN pip install -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["python3", "api/v1/app.py"]