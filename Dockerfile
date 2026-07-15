FROM node:22-bullseye

RUN apt-get update && \
    apt-get install -y python3 python3-pip

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

RUN cd whatsapp && npm install

CMD ["bash", "start.sh"]
