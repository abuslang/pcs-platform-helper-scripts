#!/usr/bin/env python3

import argparse
import requests
import json
import os
import pprint
import sys

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..', 'utilities')))
from pc_auth import *
from pc_cache import *
from pc_api import *

pp = pprint.PrettyPrinter(indent=5)

argParser = argparse.ArgumentParser()
argParser.add_argument("-v", "--verbose", action='store_true', help="Print Verbose Messages")
argParser.add_argument("-f", "--file", default="purge_accounts.json", help="Define Cache File")
argParser.add_argument("-c", "--cache", action='store_true', help="Cache Results")
argParser.add_argument("-x", "--config", action='store', help="Authorization - Config File (~/.prismacloud)", required=True)
# added this instead to read the config file from the same directory
#argParser.add_argument("-x", "--config", action='store', help="Authorization - Config File (/.prismacloud)", required=True)

args = argParser.parse_args()

config_file = os.path.join(os.path.expanduser('~/.prismacloud'), args.config)
if(args.verbose is True): print("Auth Config File >", config_file)
pc = json.loads(connect(config_file))

# Looping Defaults
items = []
page_size = 50

if args.cache:
    items = create_cache(pc, args, "/api/v1/cloud-scan-rules")

# Read from cache file
print("Read from cache file", args.file)
with open(args.file, 'r') as file:
    items = json.load(file)
if(args.verbose is True): print("Total Records in Cache: ", len(items))

def print_accounts_for_confirmation(accounts):
    """Prints the accounts to be deleted and prepares them for user confirmation."""
    account_ids = [account['credential']['accountID'] for account in accounts]
    print("The following accounts are marked as deleted and will be removed:")
    for account_id in account_ids:
        print(account_id)
    return account_ids

def get_user_confirmation():
    """Gets user confirmation to proceed with deletion."""
    confirmation = input("Do you want to proceed with deleting these accounts? (yes/no): ")
    return confirmation.lower() == 'yes'

# Filter out the deleted accounts
action_items = [item for item in items if item.get('deleted') is True]

# Print accounts for user confirmation
account_ids_to_delete = print_accounts_for_confirmation(action_items)

# Ask for user confirmation before deletion
if get_user_confirmation():
    # Perform deletion of accounts
    for account in action_items:
        account_id = account["credential"]["accountID"]
        print(f"Removing Account: {account['credential']['accountName']}")
        pc_request(auth=pc, method="delete", url=pc["twistlockUrl"] + f"/api/v1/cloud-scan-rules/{account_id}", platform=False, verbose=args.verbose)
    if(args.verbose is True): print("Total Accounts Deleted", len(action_items))
else:
    print("Operation canceled by user.")