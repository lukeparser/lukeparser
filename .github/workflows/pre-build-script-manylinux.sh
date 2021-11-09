#!/bin/bash
set -e -x

# remove old bison installation
yum remove -y bison
# install newer bison
cd /tmp
BISON=bison-3.4
curl -o bison.tar.gz http://ftp.gnu.org/gnu/bison/$BISON.tar.gz
tar -xvzf bison.tar.gz
cd $BISON
./configure --prefix=/usr/local/
make
make install
bison --version
if [ `uname -m` == "aarch64" ]; then
   for python in /opt/python/cp3*/bin/python; do
      $python -m pip install cython
   done
fi
