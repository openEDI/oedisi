FROM python:3.10.6-slim-bullseye
RUN apt-get update
RUN apt-get install -y git ssh
RUN mkdir ComponentTwo
COPY  . ./ComponentTwo
WORKDIR ./ComponentTwo
RUN pip install -r requirements.txt
EXPOSE 5679/tcp
CMD ["python", "server.py"]
