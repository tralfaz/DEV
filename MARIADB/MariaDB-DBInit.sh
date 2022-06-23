#!/bin/sh
set -x

BASEDIR=/usr/local/brion_AVX/MariaDB/5.5.53_3
DISTDIR=$BASEDIR
DATADIR=/home/mmarchio/SCRATCH/MariaDB/data


DBLCLSKT="--socket=$PWD/mariadb.sock --port=61111"


$DISTDIR/bin/mysql \
    $DBLCLSKT \
    --user=root --database=mysql
fdev060501> cat MariaDB-DBInit.sh 
#!/bin/sh
set -x

BASEDIR=/usr/local/brion_AVX/MariaDB/5.5.53_3
DISTDIR=$BASEDIR
DATADIR=/home/mmarchio/SCRATCH/MariaDB/data


DBLCLSKT="--socket=$PWD/mariadb.sock --port=61111"


$DISTDIR/bin/mysql \
    $DBLCLSKT \
    --user=root --database=mysql << EOF
CREATE USER 'hypnotoad'@'localhost' IDENTIFIED BY 'obey';
CREATE USER 'hypnotoad'@'%' IDENTIFIED BY 'mypass';
GRANT ALL ON *.* TO 'hypnotoad'@'localhost';
GRANT ALL ON *.* TO 'hypnotoad'@'%';
flush privileges;
EOF

$DISTDIR/bin/mysql \
    $DBLCLSKT \
    --user=root mysql << EOF
SELECT User, Host FROM mysql.user;
EOF

$DISTDIR/bin/mysql \
    $DBLCLSKT \
    --user=root mysql << EOF
CREATE DATABASE IF NOT EXISTS db1;
SHOW DATABASES;
EOF

exit

$DISTDIR/bin/mysql \
    $DBLCLSKT \
    --user=root mysql << EOF
GRANT ALL PRIVILEGES ON *.* TO 'root'@'192.168.100.%' 
  IDENTIFIED BY 'my-new-password' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'172.%.%.%' 
  IDENTIFIED BY 'my-new-password' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'fdev%' 
  IDENTIFIED BY 'my-new-password' WITH GRANT OPTION;
EOF

$DISISDIR/bin/mysql \
    --socket=$PWD/mariadb.sock \
    --port=61111          \
    --user=root mysql << EOF
grant all privileges on *.* to a_tachyon@'localhost' identified with auth_tflex with grant option;
grant all privileges on *.* to a_tachyon@'%' identified with auth_tflex with grant option;
grant all privileges on dummydb.* to w_tachyon@'localhost' identified with auth_tflex;
grant all privileges on dummydb.* to w_tachyon@'%' identified with auth_tflex;
grant select, lock tables on dummydb.* to r_tachyon@'localhost' identified with auth_tflex;
grant select, lock tables on dummydb.* to r_tachyon@'%' identified with auth_tflex;
grant SUPER on *.* to a_tachyon@'%' identified with auth_tflex;
grant RELOAD,SHUTDOWN on *.* to w_tachyon@'%' identified with auth_tflex;
grant RELOAD,SHUTDOWN on *.* to w_tachyon@'localhost' identified with auth_tflex;
grant SHUTDOWN on *.* to r_tachyon@'127.0.0.1' identified with auth_tflex;
grant PROXY on ''@'' to 'a_tachyon'@'%' with grant option;
grant PROXY on ''@'' to 'a_tachyon'@'localhost' with grant option;
EOF

$DISISDIR/bin/mysql --socket=$PWD/my.sock --user=root mysql -t << EOF
select User,Host,Password,plugin from mysql.user;
EOF


#$DISISDIR/bin/mysql --socket=$PWD/my.sock --port=61111 --user=root mysql -t << EOF
#delete from mysql.user where User = 'root' or User = '';
#select User,Host,Password,plugin from mysql.user;
#flush privileges;
#flush tables with read lock;
#EOF

#$DISTDIR/bin/mysql --socket=$PWD/my.sock --user=root mysql -t << EOF
#drop user 'root'@'localhost';
#EOF


#$DISTDIR/bin/mysqlcheck --socket=my.sock --user=a_tachyon -A --use-frm \
#                        --auto-repair -o --extended                    \
#                        --password='.V^onxHV6UF+5EHtllRFM.geIfcdm5by'
