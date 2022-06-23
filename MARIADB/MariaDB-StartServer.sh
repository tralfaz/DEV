#!/bin/sh
set -x


#BASEDIR=/home/mmarchio/DEV/DB/mariadb-5.5.53
#DISTDIR=$BASEDIR/dist
BASEDIR=/usr/local/brion_AVX/MariaDB/5.5.53_3
DISTDIR=$BASEDIR
DATADIR=/home/mmarchio/SCRATCH/MariaDB/data
#DATADIR=/home/mmarchio/DEV/DB/MariaDB/data

#rm -rf $DATADIR/*

$DISTDIR/scripts/mysql_install_db \
    --basedir=$DISTDIR  \
    --datadir=$DATADIR \
    --no-defaults
#--user=mmarchio \

#rm -Rf $DATADIR/[at]*

DBHOST=$(hostname)

# Start Server
#$DISTDIR/.bin/mysqld --no-defaults \
#                    --basedir=$DISTDIR --datadir=$DATADIR \
#                    --bind-address=0.0.0.0 \
#                    --port=61111 \
#                    --socket=$PWD/mariadb.sock \
#                    --pid-file=$PWD/mysqld.pid   \
#                    --log-error=$PWD/mariadb-server-${DBHOST}.log \
#                    --tmpdir=$PWD/tmp    \
#                    --skip-innodb --default-storage-engine=myisam      \
#                    --skip-xtradb --skip-aria                          \
#                    --lc-messages-dir=$DISTDIR/share                   \
#                    --lc-messages=en_US &
#--skip-bind-address \
#                    --plugin-load=libtflex_mysql_auth                  \
#                    --auth_tflex_jobroot=$PWD &
#                    --skip-xtradb --skip-aria                          \
#MDB_PID=$!
#echo "MYSQLD PID: $MDB_PID"
