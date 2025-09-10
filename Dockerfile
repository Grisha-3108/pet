FROM python:3.13.7-alpine3.22
WORKDIR /app
COPY . /app
RUN pip install uv
RUN uv export --all-groups --all-extras --format requirements.txt --no-hashes > requirements.txt
RUN pip install -r requirements.txt
RUN mkdir keys
RUN apk add openssl
RUN openssl genrsa --out ./keys/private.pem 2048
RUN openssl rsa --in ./keys/private.pem --outform PEM --pubout --out ./keys/public.pem
RUN chmod 777 ./run.sh
RUN apk add ca-certificates && update-ca-certificates
CMD ["./run.sh"]