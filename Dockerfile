FROM python:3.13.7-alpine3.22
WORKDIR /app
RUN apk add openssl
RUN apk add gcc musl-dev linux-headers
RUN pip install uv
RUN apk add ca-certificates && update-ca-certificates
RUN adduser -D application
RUN addgroup running
RUN addgroup application running
RUN mkdir keys
COPY ./uv.lock ./pyproject.toml /app
RUN uv export --all-groups --format requirements.txt --no-hashes > requirements.txt
RUN pip install -r requirements.txt
COPY . /app
RUN openssl genrsa --out ./keys/private.pem 2048
RUN openssl rsa --in ./keys/private.pem --outform PEM --pubout --out ./keys/public.pem
RUN chgrp -R running ./
RUN chmod -R 070 ./
USER application
CMD ["./run.sh"]
HEALTHCHECK --interval=60s --timeout=10s --retries=5 --start-period=60s CMD python healthcheck.py