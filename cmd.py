#!/usr/bin/env python3
import argparse
from boinc_utils import get_host_info, exchange_versions

parser = argparse.ArgumentParser()
parser.add_argument("--get_host_info", help="show host info",
                    action="store_true")
parser.add_argument("--client_version", help="show client version",
                    action="store_true")

args = parser.parse_args()

if args.get_host_info:
    get_host_info()

if args.client_version:
    exchange_versions()
