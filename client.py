import sys
from time import sleep
import json
import logging

import requests

logger = logging.getLogger(__file__)

# curl -X POST -F q=@PATH_TO_FILE -F 'mode=3diaa' -F 'database[]=afdb50' -F 'database[]=afdb-swissprot' -F 'database[]=afdb-proteome' -F 'database[]=cath50' -F 'database[]=mgnify_esm30' -F 'database[]=pdb100' -F 'database[]=gmgcl_id' https://search.foldseek.com/api/ticket

URI = 'https://search.foldseek.com/api'


def job_submit(pdb_str, mode='3diaa', databases=None):
  if databases is None:
    databases = [
        'afdb50', 'afdb-proteome', 'cath50', 'mgnify_esm30', 'pdb100',
        'gmgcl_id'
    ]
  ticket = requests.post(f'{URI}/ticket', {
      'q': pdb_str,
      'database[]': databases,
      'mode': mode,
  }).json()
  logger.debug('ticket: %s', ticket)
  return ticket


def job_status(ticket):
  status = requests.get(f'{URI}/ticket/' + ticket['id']).json()
  logger.debug('ticket: %s, status=%s', ticket, status)
  return status


def job_result(ticket):
  result = requests.get(f'{URI}/result/' + ticket['id'] + '/0').json()
  return result


def job_run(pdb_str, mode='3diaa', databases=None):
  ticket = job_submit(pdb_str, mode=mode, databases=databases)

  repeat = True
  while repeat:
    status = job_status(ticket)
    if status['status'] == "ERROR":
      # handle error
      return None

    # wait a short time between poll requests
    sleep(1)
    repeat = status['status'] != "COMPLETE"

  # get all hits for the first query (0)
  result = job_result(ticket)
  return result


def read_task_list(f):
  for line in filter(lambda x: x, map(lambda x: x.strip(), f)):
    yield line

def main(args):
  if args.task_list:
    if args.input_files is None:
      args.input_files = []
    if args.task_list == '-':
      args.input_files += list(read_task_list(sys.stdin))
    else:
      with open(args.task_list, 'r') as f:
        args.input_files += list(read_task_list(f))
  for pdb_file in args.input_files:
    with open(pdb_file, 'r') as f:
      pdb_str = f.read()
    try:
      result = job_run(pdb_str, mode=args.mode, databases=args.databases)
    except Exception as e:
      logger.error('%s\t%s', pdb_file, str(e))
    result = json.dumps(result)
    print(f'Foldseek\t{pdb_file}\t{result}')

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()

  parser.add_argument('input_files',
                      metavar='file',
                      type=str,
                      nargs='*',
                      help='input files')
  parser.add_argument('-l',
                      '--task_list',
                      default=None,
                      help='list of pdb files.')
  parser.add_argument(
      '--databases',
      type=str,
      nargs='+',
      default=None,
      help=
      'database list[afdb50, afdb-proteome, cath50, mgnify_esm30, pdb100, gmgcl_id], default=None'
  )
  parser.add_argument('--mode',
                      type=str,
                      default='3diaa',
                      choices=['3diaa', 'tmalign'],
                      help='model of prefilter, default=\'3diaa\'')
  parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
  args = parser.parse_args()

  logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

  main(args)
