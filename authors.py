#!/usr/bin/env python

import sys

from gitstats import _sh

for i in sys.stdin:
    i = i.strip()
    if not i:
        continue
    aliases = [a.strip() for a in i.split(' ')]
    if len(aliases) < 2:
        continue
    print aliases
    _sh('python gitstats.py rename_author %s' % ' '.join(aliases))
