FROM python:2.7
LABEL maintainer="Sebastien Bodrero"

COPY techtrends /app
WORKDIR /app

RUN pip install -r requirements.txt

RUN chmod +x ./init.sh

EXPOSE 3111

# command to run on container start
CMD ["bash", "./init.sh"]
