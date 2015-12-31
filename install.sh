#!/usr/bin/env sh

# There may be things missing here, or things that are here but aren't needed anymore.

sudo apt-get update

sudo apt-get install daemon \
                     exiftool \
                     libavcodec-dev \
                     libavformat-dev \
                     libavutil-dev \
                     libjpeg-dev \
                     libmtp-dev \
                     libswscale-dev \
                     lighttpd \
                     mtp-tools \
                     python \
                     python-dev \
                     python-pip \
                     screen

sudo pip install configparser \
                 funcsigs \
                 mock \
                 pbr \
                 pillow \
                 python-dateutil \
                 python-firebase \
                 requests

# ExifTool Wrapper
git clone https://github.com/smarnach/pyexiftool.git /tmp/pyexiftool
cd /tmp/pyexiftool && sudo python setup.py install

# Compile/install ffmpeg from src
# https://www.bitpi.co/2015/08/19/how-to-compile-ffmpeg-on-a-raspberry-pi/