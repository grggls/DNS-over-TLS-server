FROM python:3.11-alpine
ARG STUB
ENV STUB ${STUB}

# Install system dependencies
RUN apk --update add --no-cache \
    alpine-sdk \
    libcurl \
    curl-dev \
    curl \
    git \
    knot-utils \
    && git clone https://github.com/curl/doh && \
    cd doh && make && mv /tmp/doh/doh /usr/local/bin/doh && \
    rm -rf /tmp/doh

# Install Rye
RUN pip install rye

WORKDIR /srv
COPY pyproject.toml rye.lock ./
RUN rye sync --no-dev

COPY . .
RUN rye sync --no-dev

RUN addgroup -g 942 srv && \
    adduser -S -u 942 -h /srv/ -s /sbin/nologin -D -H srv srv
USER srv

CMD rye run dns-over-tls-server -p 8053 -c 3 -s ${STUB}
EXPOSE 8053
