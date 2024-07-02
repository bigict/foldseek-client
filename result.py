import hashlib
import sys
import re
import json


def lines(f):
  for line in filter(lambda x: len(x) > 0, map(lambda x: x.strip(), f)):
    key, value = line.split('\t', 1)
    yield key, json.loads(value)

def out(key, idx, obj):
  sequence = obj['queries'][idx]['sequence']
  for r in obj['results']:
    if r['alignments']:
      for i, align in enumerate(r['alignments'][idx]):
        print(f"{key}\t{idx}\t{i}\t{sequence}\t{r['db']}\t{align['eval']}\t{align['score']}\t{align['target']}")

for key, obj in lines(sys.stdin):
  while isinstance(obj, str):
    obj = json.loads(obj)

  if isinstance(obj, list):
    for i in range(len(obj)):
      out(key, i, obj[i])
  elif isinstance(obj, dict):
    for i in range(len(obj['queries'])):
      out(key, i, obj)
