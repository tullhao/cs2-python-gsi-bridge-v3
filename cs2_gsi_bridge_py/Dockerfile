FROM python:3.12-alpine

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app
RUN chmod +x /run.sh
COPY run.sh /run.sh

CMD ["/run.sh"]
