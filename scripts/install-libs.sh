#!/bin/bash

export LIBRDKAFKA_VERSION=0.11.4
export OPENSSL_VER=1.0.2o
export PREFIX=/opt/build-libs

mkdir /tmp/openssl && cd $_ && \
  curl -L https://www.openssl.org/source/openssl-$OPENSSL_VER.tar.gz | \
  tar xz --strip-components=1 && \
  ./config --prefix=$PREFIX zlib no-krb5 zlib shared && \
  make && make install

mkdir /tmp/librdkafka && cd $_ && \
  curl -L https://github.com/edenhill/librdkafka/archive/v$LIBRDKAFKA_VERSION.tar.gz | \
  tar xz --strip-components=1 && \
  ./configure --prefix=$PREFIX && \
  make && make install
