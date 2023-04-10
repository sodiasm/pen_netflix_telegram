import os
from telegram import Message, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser
import logging
import pyodbc

# bot_msg 0,1,2 = go ahead; 3,4,5 = topic finished
question_id = -1
film_name = ""

bot_msg = [
    'Hi, what film do you like?',
    'Have you watched it? (yes/no)',
    'Please write your review of %s.',
    'Thanks for your review of %s.',
    'Let\'s see a review from other people.',
    'Opss... Nobody leaves any reviews.'
]
bot_expt_msg = 'I don\'t know what are you saying.'

server = os.environ['server']
database = os.environ['database']
username = os.environ['username']
password = os.environ['password']
driver=os.environ['driver']
conn_str = 'DRIVER='+driver+';ENCRYPT=yes;SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password

def main():  
    # Load your token and create an Updater for your Bot
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', start))
    # To start the bot:
    updater.start_polling()
    updater.idle()
    
def start(update, context):
    question_id = 0
    context.bot.send_message(chat_id=update.effective_chat.id, text=bot_msg[0])
    return

def echo(update, context):
    global question_id
    global film_name
    if question_id == 0:
        film_name = update.message.text
        question_id = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text=bot_msg[1])
    elif question_id == 1:
        if update.message.text.lower() == "no":
            res = query_db("SELECT top 1 review FROM films where film_name = ? order by NEWID() ", film_name)
            film_name = ""
            question_id = -1
            context.bot.send_message(chat_id=update.effective_chat.id, text=bot_msg[4])
            if res == None:
                context.bot.send_message(chat_id=update.effective_chat.id, text=res[5])
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=res[0])
            return
        elif update.message.text.lower() == "yes":
            question_id = 2
            reply_message = bot_msg[2] % (film_name)
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
            return
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=bot_expt_msg)
            return
    elif question_id == 2:
        res = query_db("SELECT * FROM films where userid = ? and film_name = ? ", (str(update.effective_chat.id),film_name,) )
        if res == None:
            query_update_delete_db("INSERT INTO films (film_name, userId, review) VALUES (?, ?, ?)", (film_name ,str(update.effective_chat.id) , update.message.text, ))
        else:
            query_update_delete_db("Update films Set review = ? where userid = ? and film_name = ?", (update.message.text , str(update.effective_chat.id) , film_name, ))
        reply_message = bot_msg[3] % (film_name)
        film_name = ""
        question_id = -1
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
        return
    else:
        question_id = 0
        context.bot.send_message(chat_id=update.effective_chat.id, text=bot_msg[0])
    return 
    
def query_db(query, value):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query,value) 
            return cursor.fetchone()
        
def query_update_delete_db(query, value):
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query,value) 
            conn.commit()
            return cursor.rowcount
        
if __name__ == '__main__':
    main()
