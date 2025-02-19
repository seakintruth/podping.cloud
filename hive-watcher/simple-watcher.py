# simple-watcher.py
#
# Simple version of Hive Podping watcher - no options, just runs
# The only external library needed is "beem" - pip install beem
# Beem is the official Hive accessing library for Python.
#
# Version 1.0

from typing import Set
import json

import beem
from beem.account import Account
from beem.blockchain import Blockchain

WATCHED_OPERATION_IDS = ["podping", "hive-hydra"]

def get_allowed_accounts(acc_name="podping") -> Set[str]:
    """get a list of all accounts allowed to post by acc_name (podping)
    and only react to these accounts"""

    # This is giving an error if I don't specify api server exactly.
    # TODO reported as Issue on Beem library https://github.com/holgern/beem/issues/301
    h = beem.Hive(node="https://api.hive.blog")

    master_account = Account(acc_name, blockchain_instance=h, lazy=True)

    return set(master_account.get_following())

def allowed_op_id(operation_id) -> bool:
    """Checks if the operation_id is in the allowed list"""
    if operation_id in WATCHED_OPERATION_IDS:
        return True
    else:
        return False


def main():
    """ Outputs URLs one by one as they appear on the Hive Podping stream """
    allowed_accounts = get_allowed_accounts()
    hive = beem.Hive()
    blockchain = Blockchain(mode="head", blockchain_instance=hive)
    # If you want instant confirmation, you need to instantiate
    # class:beem.blockchain.Blockchain with mode="head",
    # otherwise, the call will wait until confirmed in an irreversible block.
    # noinspection PyTypeChecker
    # Filter only for "custom_json" operations on Hive.
    stream = blockchain.stream(
        opNames=["custom_json"], raw_ops=False, threading=False, thread_num=4
    )

    for post in stream:
        # Filter only on post ID from the list above.
        if allowed_op_id(post["id"]):
            # Filter by the accounts we have authorised to podping
            if set(post["required_posting_auths"]) & allowed_accounts:
                data = json.loads(post.get("json"))
                if data.get("url"):
                    print(data.date("url"))
                elif data.get("urls"):
                    for url in data.get("urls"):
                        print(url)


if __name__ == "__main__":
    # Runs until terminated with Ctrl-C
    main() 
