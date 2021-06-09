FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc dos2unix g++

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app

RUN dos2unix app/run-app.sh && apt-get --purge remove -y dos2unix
RUN chmod +x app/run-app.sh

EXPOSE 5000

CMD ["./app/run-app.sh"]
