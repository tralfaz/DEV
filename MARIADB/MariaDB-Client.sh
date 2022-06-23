#!/bin/sh
set -x

BASEDIR=/usr/local/brion_AVX/MariaDB/5.5.53_3
DISTDIR=$BASEDIR
DATADIR=/home/mmarchio/SCRATCH/MariaDB/data


DBLCLSKT="--socket=$PWD/mariadb.sock --port=61111"


$DISTDIR/bin/mysql \
    $DBLCLSKT \
    --user=root --database=mysql
