#!/bin/sh
set -x

SCRIPTDIR="$(dirname "$0")"
MDBPIDPATH="${SCRIPTDIR}/mysqld.pid"
if [ -e "$MDBPIDPATH" ]; then
  MDBPID="$(cat "$MDBPIDPATH")"
  ps -p $MDBPID > /dev/null
  if [ "$?" != "0" ]; then
    echo "Process $MDBPID not found."
  else
    echo "Stopping $MDBPID ..."
    kill -9 $MDBPID
  fi
 
else
  MDBPID=-1
fi
