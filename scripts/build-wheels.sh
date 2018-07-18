#!/bin/bash

for PYBIN in /opt/python/*/bin; do
  $PYBIN/pypy setup.py bdist_wheel -d pypy-dist
done

for whl in $(ls pypy-dist/*.whl); do
  LD_LIBRARY_PATH=/usr/local/lib \
  /opt/python/pp360/bin/auditwheel repair -w pypy-wheelhouse $whl
done
