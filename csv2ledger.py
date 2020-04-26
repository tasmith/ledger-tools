#! env python

import sys
from sys import argv
import csv
from pathlib import Path
import hashlib
from string import Template
import argparse
import re

PROGRAM = 'csv2ledger'
VERSION_STRING = '%(prog)s 0.0.0'
LIMIT = 4

# re to remove comments in config file, but allow # to be quoted with [#]
COMMENT_SPLIT_RE = re.compile(r'#.(?<!\[#\])|#$')

def info(cmd):
    version(cmd)
    print(f'* INFO: using Python {sys.version}')


def date_to_ISO(date):
    d, m, y = date.split('/')
    if len(y) == 2 and int(y) <= 30:
        y = '20' + y
    if len(m) == 1:
        m = '0' + m
    if len(d) == 1:
        d = '0' + d
    return '-'.join([y, m, d])


def print_multiline(tag, text):
    lines = [part.strip() for part in text.split('\n') if part.strip()]
    if len(lines) > 0:
        print(f'{tag:9s}: {lines[0]}')
    for ln in lines[1:]:
        print(f'           {ln}')


def print_ledger_entry(fields, row, account):
    flatrow = [txt.replace('\n','|').replace('\r','') for txt in row]
    d = dict(zip(fields, flatrow))
    date = d['date']
    desc = d['desc']
    amt = d['amt']
    details = d['details']
    csv = ','.join(flatrow)
    print(f"{date}  {desc}")
    if details != desc:
        print(f"      ; {details}")
    print(f"    {'Liabilities:AMEX-3009':45s}{amt}")
    print(f"    {account}")
    print()

def print_needs_account(fields, row):
    for field, text in zip(fields, row):
        print_multiline(field, text)

def print_transaction(fields, row, patterns):
    for field, text in zip(fields, row):
        for account, pat in patterns[field]:
            if re.match(pat, text):
                print_ledger_entry(fields, row, account)
                return
    print_needs_account(fields,row)
    print("Quit, after unknown expense in transaction")
    exit()

def config_reader(f):
    for line in f:
        # remove trailing white space and comments
        left = re.split(COMMENT_SPLIT_RE, line)[0]
        line = left.rstrip()
        if len(line) == 0:
            continue
        yield line


def main(args):
    verbose = args.verbose
    infile = args.FILE
    config = config_reader(args.CONFIG)

    date_format = next(config)
    expected_heading = next(config)
    fields = next(config).split(',')

    patterns = dict()
    for f in fields:
        patterns[f] = []

    account = "Expenses:Unknown"
    accountset = {account}

    for line in config:
        if not line[0].isspace():
            account = line
            if account in accountset:
                error_exit(f"Duplicate account in config file: {account}")
        else:
            field, space, regex = line.lstrip().partition(' ')
            patterns[field].append((account, regex))

    input_heading = infile.readline().strip()

    if input_heading != expected_heading:
        error_exit("input file and configuration file expected heading don't match")

    csvreader = csv.reader(infile)
    for row in csvreader:
        print_transaction(fields, row, patterns)
        print()
        print()

def parse_command_args():
    parser = argparse.ArgumentParser(prog='csv2ledger')
    parser.add_argument('-v', '--version', action='version', version=VERSION_STRING)
    parser.add_argument('-V', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('--one-line', help='convert csv to single line csv only')
    parser.add_argument('CONFIG', type=open)
    parser.add_argument('FILE', type=lambda f: open(f, newline=''))

    return parser.parse_args()


def error_exit(msg):
    print(f'{PROGRAM}: {msg}', file=sys.stderr)
    exit(1)

if __name__ == '__main__':
    args = parse_command_args()
    main(args)
