FROM python:3.11.5-slim
WORKDIR /app
RUN python3 -m pip install pip --upgrade
RUN apt update -y
RUN apt install celery -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN pip3 install celery
RUN chmod +x entrypoint.sh




