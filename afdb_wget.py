import json
from pathlib import Path
import re

import requests


# MMCIF_URI = "https://alphafold.ebi.ac.uk/files/AF-%s-F1-model_v4.cif"
# PAE_URI = "https://alphafold.ebi.ac.uk/files/AF-%s-F1-predicted_aligned_error_v4.json"
FOLDSEEK_URI = "https://www.alphafold.ebi.ac.uk/api/cluster/members/%s?cluster_flag=AFDB%2FFoldseek&records=10&start=0&sort_direction=DESC&sort_column=averagePlddt"

def uri_fetch(uri, retry=3):
  retry = 1 if retry <= 0 else retry

  print(f"wget {uri} retry={retry}")
  while retry > 0:
    try:
      r = requests.get(uri)
      if r.status_code == 200:
        return r.text
    except:
      print(f"wget {uri} retry={retry}")
    retry -= 1
  return None

def prediction_fetch(pid):
  text = uri_fetch(f"https://alphafold.ebi.ac.uk/api/prediction/{pid}")
  if text:
    yield from json.loads(text)

def foldseek_fetch(uid):
  text = uri_fetch(f"https://www.alphafold.ebi.ac.uk/api/cluster/members/{uid}?cluster_flag=AFDB%2FFoldseek&records=10&start=0&sort_direction=DESC&sort_column=averagePlddt")
  if text:
    obj = json.loads(text)
    if "clusterMembers" in obj and "afdbAccessions" in obj["clusterMembers"]:
      for pid in obj["clusterMembers"]["afdbAccessions"]:
        m = re.match("AF-(.+)-F1", pid)
        if m and m.group(1) != uid:
          yield m.group(1)

def afdb_fetch(args, pid, recursive=False):
  n = 0
  for pred_obj in prediction_fetch(pid):
    uid = pred_obj["uniprotAccession"]
    seq = pred_obj["uniprotSequence"]
    ver = pred_obj["latestVersion"]
    cif = uri_fetch(pred_obj["cifUrl"])
    if cif:
      with open(args.output_dir / "mmcif" / f"{uid}.cif", "w") as f:
        f.write(cif)
    pae = uri_fetch(pred_obj["paeDocUrl"])
    if pae:
      with open(args.output_dir / "npz" / f"{uid}-predicted_aligned_error.json", "w") as f:
        f.write(pae)
    if recursive:
      for pid in foldseek_fetch(uid):
        afdb_fetch(args, pid, recursive=False)
    print(pred_obj)
    n += 1
  return n

def main(args):
  args.output_dir.mkdir(parents=True, exist_ok=True)
  for entry in ("mmcif", "npz"):
    (args.output_dir / entry).mkdir(exist_ok=True)

  for pid in args.pid:
    for uid in pid.split(','):
      if afdb_fetch(args, uid, recursive=args.recursive) > 0:
        break
    
if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("pid", type=str, nargs="+", help="uniprot protein id.")
  parser.add_argument("-o", "--output_dir", type=Path, default=".",
                      help="output dir.")
  parser.add_argument("-R", "--recursive", action="store_true",
                      help="recursive.")
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="verbose.")

  args = parser.parse_args()

  main(args)
