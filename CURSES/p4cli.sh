python ./p4climenu.py
P4CLIENTCHOICE="$(cat ~/.p4clientchoice.out)"
if [ "$P4CLIENTCHOICE" != "" ]; then
  export P4CLIENT="$P4CLIENTCHOICE"
fi
