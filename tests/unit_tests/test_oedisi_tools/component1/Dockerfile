FROM python:3.10.6-slim-bullseye
RUN apt-get update
RUN apt-get install -y git ssh
RUN mkdir ComponentOne
COPY  . ./ComponentOne
WORKDIR ./ComponentOne
RUN pip install -r requirements.txt
EXPOSE 5678/tcp
CMD ["python", "server.py"]
