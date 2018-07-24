#!/bin/bash

export CFLAGS="-I/opt/build-libs/include"
export LDFLAGS="-L/opt/build-libs/lib"

/opt/pypy-6.0.0/bin/pypy setup.py sdist
for env in $PYENVS; do
  CFLAGS="-I/opt/build-libs/include" \
  LDFLAGS="-L/opt/build-libs/lib" \
  /opt/$env/bin/pypy setup.py bdist_wheel
done

for whl in $(ls dist/*.whl); do
  LD_LIBRARY_PATH=/opt/build-libs/lib \
  /opt/pypy3.5-6.0.0/bin/auditwheel repair $whl
done
