FROM python:3-alpine
COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev libxslt-dev libxml2-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scrapyd.conf /etc/scrapyd/
VOLUME /etc/scrapyd/ /var/lib/scrapyd/
EXPOSE 6800

CMD ["scrapyd", "--pidfile="]
