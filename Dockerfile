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
RUN apk add --no-cache flac ffmpeg python2
RUN pip install pywikibot requests-oauthlib
CMD /bin/sh
