import hashlib
import sys
import re
import json


def lines(f):
  for line in filter(lambda x: len(x) > 0, map(lambda x: x.strip(), f)):
    key, value = line.split('\t', 1)
    yield key, json.loads(value)


for key, obj in lines(sys.stdin):
  sequence = obj['query']['sequence']
  for r in obj['results']:
    if r['alignments']:
      for align in r['alignments']:
        print(f"{key}\t{sequence}\t{r['db']}\t{align['target']}")
