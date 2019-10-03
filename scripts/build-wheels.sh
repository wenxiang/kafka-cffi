#!/bin/bash

echo 'Checking git status inside the container'
git status

echo 'Checking git describe'
git describe

for PYBIN in /opt/python/*/bin; do
  echo "Checking version with $PYBIN/pypy"
  $PYBIN/pypy setup.py --version
  $PYBIN/pypy setup.py bdist_wheel -d pypy-dist
done

for whl in $(ls pypy-dist/*.whl); do
  LD_LIBRARY_PATH=/usr/local/lib \
  /opt/python/pp360/bin/auditwheel repair -w pypy-wheelhouse $whl
done
