#!/usr/bin/env python
from collections import Counter
import json
import logging
import telebot
from argparse import ArgumentParser
from pymongo import MongoClient
from datetime import datetime, timedelta

HELP = """*No Sticker Bot Help*

This simple telegram bot was created to solve only one task - to delete FUCKINGLY annoying stickers. Since you add bot to the group and allow it to sticker messages it starts deleting any sticker posted to the group.

*Usage*

1. Add [@ozone_nosticker_bot](https://t.me/ozone_nosticker_bot) to your group.
2. Go to group settings / users list / promote user to admin
3. Enjoy!

*Commands*

/help - display this help message
/stat - display simple statistics about number of deleted stickers

*Open Source*

*Questions, Feedback*
[@ozonecoders](https://t.me/ozonecoders)

"""

def create_bot(api_token, db):
    bot = telebot.TeleBot(api_token)

    @bot.message_handler(content_types=['sticker'])
    def handle_sticker(msg):
        bot.delete_message(msg.chat.id, msg.message_id)
        db.event.save({
            'type': 'delete_sticker',
            'chat_id': msg.chat.id,
            'chat_username': msg.chat.username,
            'user_id': msg.from_user.id,
            'username': msg.from_user.username,
            'date': datetime.utcnow(),
        })

    #@bot.message_handler(content_types=['document'])
    #def handle_document(msg):
    #    if msg.document.mime_type == 'video/mp4':
    #        bot.delete_message(msg.chat.id, msg.message_id)
    #        db.event.save({
    #            'type': 'delete_document',
    #            'chat_id': msg.chat.id,
    #            'chat_username': msg.chat.username,
    #            'user_id': msg.from_user.id,
    #            'username': msg.from_user.username,
    #            'date': datetime.utcnow(),
    #            'document': {
    #                'file_id': msg.document.file_id,
    #                'file_name': msg.document.file_name,
    #                'mime_type': msg.document.mime_type,
    #                'file_size': msg.document.file_size,
    #                'thumb': msg.document.thumb.__dict__ if msg.document.thumb else None,
    #            },
    #        })


    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(msg):
        if msg.chat.type == 'private':
            bot.reply_to(msg, HELP, parse_mode='Markdown')
        else:
            if msg.text.strip() in (
                    '/start', '/start@ozone_nosticker_bot', '/start@nosticker_test_bot',
                    '/help', '/help@ozone_nosticker_bot', '/help@nosticker_test_bot'
                ):
                bot.delete_message(msg.chat.id, msg.message_id)

    @bot.message_handler(commands=['stat'])
    def handle_stat(msg):
        if msg.chat.type != 'private':
            if msg.text.strip() in (
                    '/stat', '/stat@ozone_nosticker_bot', '/stat@nosticker_test_bot',
                ):
                bot.delete_message(msg.chat.id, msg.message_id)
            return
        days = []
        top_today = Counter()
        top_ystd = Counter()
        top_week = Counter()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for x in range(7):
            day = today - timedelta(days=x)
            query = {'$and': [
                {'type': 'delete_sticker'},
                {'date': {'$gte': day}},
                {'date': {'$lt': day + timedelta(days=1)}},
            ]}
            num = 0
            for event in db.event.find(query):
                num += 1
                key  = (
                    '@%s' % event['chat_username'] if event['chat_username']
                    else '#%d' % event['chat_id']
                )
                if day == today:
                    top_today[key] += 1
                if day == (today - timedelta(days=1)):
                    top_ystd[key] += 1
                top_week[key] += 1
            days.insert(0, num)
        ret = 'Recent 7 days: %s' % ' | '.join([str(x) for x in days])
        ret += '\n\nTop today (%d):\n%s' % (
            len(top_today),
            '\n'.join('  %s (%d)' % x for x in top_today.most_common(10)
        ))
        ret += '\n\nTop yesterday (%d):\n%s' % (
            len(top_ystd),
            '\n'.join('  %s (%d)' % x for x in top_ystd.most_common(10)
        ))
        ret += '\n\nTop 10 week:\n%s' % '\n'.join('  %s (%d)' % x for x in top_week.most_common(10))
        bot.reply_to(msg, ret)

    return bot



def main():
    parser = ArgumentParser()
    parser.add_argument('--mode')
    opts = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    token = os.environ['API_KEY']
    db = MongoClient()['nosticker']
    bot = create_bot(token, db)
    bot.polling()


if __name__ == '__main__':
    main()
