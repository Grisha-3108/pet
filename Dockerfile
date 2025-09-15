FROM python:3.13.7-alpine3.22
WORKDIR /app
COPY . /app
RUN pip install uv
RUN uv export --no-dev --format requirements.txt --no-hashes > requirements.txt
RUN pip install -r requirements.txt
RUN mkdir keys
RUN apk add openssl
RUN openssl genrsa --out ./keys/private.pem 2048
RUN openssl rsa --in ./keys/private.pem --outform PEM --pubout --out ./keys/public.pem
RUN apk add ca-certificates && update-ca-certificates
RUN adduser -D application
RUN addgroup running
RUN addgroup application running
RUN chgrp -R running ./
RUN chmod -R 070 ./
USER application
CMD ["./run.sh"]