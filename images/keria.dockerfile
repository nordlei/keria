ARG IMAGE_PYTHON_VERSION=3.10
FROM python:${IMAGE_PYTHON_VERSION}-alpine AS builder
ARG IMAGE_PYTHON_VERSION

RUN apk --no-cache add \
    bash \
    alpine-sdk \
    libffi-dev \
    libsodium \
    libsodium-dev

SHELL ["/bin/bash", "-c"]

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

WORKDIR /keria

RUN pip install --upgrade pip && python -m venv venv
ENV PATH="/keria/venv/bin/:~/.cargo/bin:${PATH}"

COPY requirements.txt requirements-freeze.txt setup.py ./
RUN mkdir /keria/src && pip install -r requirements.txt -r requirements-freeze.txt

FROM python:${IMAGE_PYTHON_VERSION}-alpine AS runner
ARG IMAGE_PYTHON_VERSION

RUN apk --no-cache add \
    bash \
    alpine-sdk \
    libsodium-dev

WORKDIR /keria

COPY --from=builder /keria /keria

RUN mkdir -p /usr/local/var/keri

COPY src/ src/

ENV PATH="/keria/venv/bin/:${PATH}"
ENTRYPOINT [ "keria" ]
CMD [ "start" ]
