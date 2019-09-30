#!/bin/bash
set -e -x

# Install a system package required by our library
yum install -y atlas-devel flex

# install newer bison
cd /tmp
BISON=bison-3.4
curl -o bison.tar.gz http://ftp.gnu.org/gnu/bison/$BISON.tar.gz
tar -xvzf bison.tar.gz
cd $BISON
./configure --prefix=/usr/local/bison --with-libiconv-prefix=/usr/local/libiconv/
make
make install
PATH=/usr/local/bison/bin:$PATH
bison --version

# drop support for python 2.7 and 3.4
\rm -rf /opt/python/cp27*
\rm -rf /opt/python/cp34*

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install -r /io/requirements.txt
    "${PYBIN}/pip" wheel /io/ -w dist/
done

# Bundle external shared libraries into the wheels
for whl in dist/*.whl; do
    auditwheel repair "$whl" --plat $PLAT -w /io/dist/
done

# Install packages and test
for PYBIN in /opt/python/*/bin/; do
    echo "$PYBIN"
    "${PYBIN}/pip" install lukeparser --no-index -f /io/dist
    # (cd "$HOME"; "${PYBIN}/nosetests" pymanylinuxdemo)
done

# use last python to pack sdist
cd /io
/opt/python/cp37-cp37m/bin/python setup.py sdist
