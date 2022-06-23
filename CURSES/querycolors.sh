#!/bin/sh
#
# Query a property from the terminal, e.g. background color
#
# XTerm Operating Systems Commands
#       "ESC ] Ps;Pt ST"

oldstty = $(stty -g)

# What to query?
# 11: text background
Ps=$(1:-11)

stty raw -echo min 0 time 0
# stty raw -echo min 0 time 1
printf "\033]$Ps;?\033\\"
# xterm needs to sleep (or "time 1", but that is 1/10th second).
sleep 0.00000001
read -r answer
#  eco $answer | cat -A
result=${answer#*;}
stty $oldstty
# Remove escape at end
echo $result | sed 's/[^rgb:0-9a-f/]\+$//'
