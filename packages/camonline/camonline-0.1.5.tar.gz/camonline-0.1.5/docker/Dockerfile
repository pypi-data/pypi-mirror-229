FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    tini ffmpeg x264 libx264-dev \
    && rm -rf /var/lib/apt/lists/*

ARG PACKAGE_VERSION

RUN pip install camonline==${PACKAGE_VERSION} --no-cache-dir

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["camonline", "start"]
