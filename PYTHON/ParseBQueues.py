import re

out1 = 'QUEUE_NAME     PRIO      STATUS      MAX  JL/U JL/P JL/H NJOBS  PEND  RUN  SUSP\ntflex           30    Open:Active      -    -    -    -     0     0     0     0 \n'

out2 = 'QUEUE_NAME     PRIO      STATUS      MAX  JL/U JL/P JL/H NJOBS  PEND  RUN  SUSP\nnormal2         35    Open:Active      -    -    -    -     0     0     0     0 \n'


out3 = 'QUEUE_NAME     PRIO      STATUS      MAX  JL/U JL/P JL/H NJOBS  PEND  RUN  SUSP\nnormal2         35    Open:Active      -    -    -    -     0     0     0     0 \nnormal          30    Open:Active      -    -    -    -    26     0    26     0 \ntflex           30    Open:Active      -    -    -    -     0     0     0     0 \ntflex hold123456789ABCDEFGHIJ 30    Open:Active      -    -    -    -     0     0     0     0 \n'


bqueuesRE = re.compile(r'(?P<name>.+) +(?P<prio>\d+) +'  \
                       r'(?P<open>\w+):(?P<active>\w+) +(?P<max>-|\\d+) +' \
                       r'(?P<jlu>-|\d+) +(?P<jlp>-|\d+) +(?P<jlh>-|\d+) +' \
                       r'(?P<njobs>\d+) +(?P<pend>\d+) +(?P<run>\d+) +'    \
                       r'(?P<susp>\d+)')


def parse_bqueues(output):
    lines = output.split('\n')
    print "LINES: %r" % lines
    for line in lines[1:]:
        if line:
            print "L: %r" % line
            match = bqueuesRE.search(line)
            if match:
                print "name: '{name}'\n" \
                      "prio: '{prio}'\n" \
                      "open: '{open}'\n" \
                      "active: '{active}'\n" \
                      "max: '{max}'\n" \
                      "jlu: '{jlu}'\n" \
                      "jlp: '{jlp}'\n" \
                      "jlh: '{jlh}'\n" \
                      "njobs: '{njobs}'\n" \
                      "pend: '{pend}'\n" \
                      "run: '{run}'\n" \
                      "susp: '{susp}'\n".format(**match.groupdict())


parse_bqueues(out1)
parse_bqueues(out2)
parse_bqueues(out3)
