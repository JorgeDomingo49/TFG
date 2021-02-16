FROM python:3-alpine
COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev libxslt-dev libxml2-dev curl git
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python"]
