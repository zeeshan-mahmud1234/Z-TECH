FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y wget unzip chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PATH="/usr/lib/chromium/:$PATH"
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

CMD ["python", "bot_scraper_received.py"] 