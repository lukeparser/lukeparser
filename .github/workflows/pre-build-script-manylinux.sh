#!/bin/bash
set -e -x

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
