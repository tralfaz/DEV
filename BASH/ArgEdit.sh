#!/bin/sh
#set -x
echo "ARGV $@"
#echo "ARGV[0] ${@[0]}"
#foo=(one 'two three')
#for arg in ${foo[@]}; {
#  echo "ARG: $arg"
#}

#allThreads=(100 200 300 400)
#for i in ${!allThreads[@]}; do
#  echo "THR: ${allThreads[$i]}"
#done

function force_avx_zero() {
  local avxzero hasavxopt=-
  echo "$1" | grep -q 'avx='
  if [ $? -eq 0 ]; then
    hasavxopt=1
    avxzero="$(echo $1 | sed -e "s/avx=1/avx=0/")"
    avxzero="$(echo "$avxzero" | sed -e "s/avx=2/avx=0/")"
  else
    avxzero="avx=0,$1"
  fi
  echo "$avxzero"
}

ARGV=()
while [ "$1" != "" ]; do
  ARGV+=("$1")
  if [ "$1" = "-O" ]; then
    jobopts="$(force_avx_zero "$2")"
    echo "JOBOPTS: $jobopts"
    ARGV+=("$jobopts")
    shift
  fi
  shift
done
#set +x

echo "ARGV: ${ARGV[@]}"
echo "ARGC: ${#ARGV[@]}"
for i in ${!ARGV[@]}; do
  echo "ARG[$i] ${ARGV[$i]}"
done

ArgEditProg.sh "${ARGV[@]}"
