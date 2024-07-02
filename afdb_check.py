import os
import sys
from pathlib import Path

def lines(f):
  for line in filter(lambda x: len(x) > 0, map(lambda x: x.strip(), f)):
    k, *v = line.split()
    v = ",".join(v)
    if v:
      yield k, v.split(",")

def check(uid_list, args):
  for uid in uid_list:
    if os.path.exists(
        os.path.join(args.output_dir, "npz", f"{uid}-predicted_aligned_error.json")):
      return True
  return False

def main(args):
  for pid, uid_list in lines(sys.stdin):
    if check(uid_list, args):
      print(f"{pid}\t1")
    else:
      print(f"{pid}\t0")
    
if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("-o", "--output_dir", type=Path, default=".",
                      help="output dir.")
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="verbose.")

  args = parser.parse_args()

  main(args)
