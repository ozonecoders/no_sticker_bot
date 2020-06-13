#!/usr/bin/env python3
import json
import logging
from argparse import ArgumentParser

from pymongo import MongoClient
from nosticker_bot import create_bot


def main():
    parser = ArgumentParser()
    parser.add_argument('--mode')
    parser.add_argument('chat_id', type=int)
    opts = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    token = os.environ['API_KEY']
    db = MongoClient()['nosticker']
    bot = create_bot(token, db)
    res = bot.leave_chat(opts.chat_id)


if __name__ == '__main__':
    main()
