# Copyright (c) 2018 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT
#
# Dockerfile for running the toolchain in a Linux container
#
# $ docker build -t pronunbot .
#
# $ docker run --mount type=bind,source="$(pwd)",target=/pronunbot      \
#   --mount type=bind,source="$(pwd)/../recordings",target=/recordings  \
#   --workdir /pronunbot -it pronunbot

FROM python:3.7.1-alpine3.8
RUN apk add --no-cache flac ffmpeg git
RUN pip install requests requests-oauthlib
RUN git clone --recursive https://gerrit.wikimedia.org/r/pywikibot/core.git pywikibot
CMD /bin/sh
