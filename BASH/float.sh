# compare via awk
numCompare() {
   awk -v n1="$1" -v n2="$2" 'BEGIN {printf "%s " (n1<n2?"<":">=") " %s\n", n1, n2}'
}

numCompare 5.65 3.14e-22
5.65 >= 3.14e-22

numCompare 5.65e-23 3.14e-22
5.65e-23 < 3.14e-22

numCompare 3.145678 3.145679
3.145678 < 3.145679


# Pure bash
if [ ${FOO%.*} -eq ${BAR%.*} ] && [ ${FOO#*.} \> ${BAR#*.} ] || [ ${FOO%.*} -gt ${BAR%.*} ]; then
  echo "${FOO} > ${BAR}";
else
  echo "${FOO} <= ${BAR}";
fi
