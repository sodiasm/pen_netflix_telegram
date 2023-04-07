import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import configparser
import logging

import pyodbc

global redis1

film_name = ""
input_review = False
config = configparser.ConfigParser()
server = ""
database = ""
username = ""
password = ""
driver = ""

def main():  
    global config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    global server
    global database 
    global username
    global password
    global driver
    server = (config['AZURE_SQL_SERVER']['server'])
    database = (config['AZURE_SQL_SERVER']['database'])
    username = (config['AZURE_SQL_SERVER']['username'])
    password = (config['AZURE_SQL_SERVER']['password'])
    driver = (config['AZURE_SQL_SERVER']['driver'])
    
    # Load your token and create an Updater for your Bot
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    
    # global redis1
    # redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
    # redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']), port=(os.environ['REDISPORT']))
    # You can set this logging module, so you will know when and why things do not work as expected Updating the Redis Server
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    # To start the bot:
    updater.start_polling()
    updater.idle()
    
def echo(update, context):
    global film_name
    global input_review
    if update.message.text.lower() == "no":
        res = query_db("SELECT top 1 review FROM films where film_name = ? order by NEWID() ", film_name )
        context.bot.send_message(chat_id=update.effective_chat.id, text= res[0])
        film_name = ""
        return
    elif update.message.text.lower() == "yes":
        input_review = True
        reply_message = 'Please write your review of ' + film_name + '.'
        context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
        return
    if(input_review == True):
        reply_message = 'Your review of ' + film_name + ' has inserted in system.'
        res = query_db("SELECT * FROM films where userid = ? and film_name = ? ", (str(update.effective_chat.id),film_name,) )
        if res == None:
            query_update_delete_db("INSERT INTO films (film_name, userId, review) VALUES (?, ?, ?)", (film_name ,str(update.effective_chat.id) , update.message.text, ))
        else:
            query_update_delete_db("Update films Set review = ? where userid = ? and film_name = ?", (update.message.text , str(update.effective_chat.id) , film_name, ))
        film_name = ""
        input_review = False
        context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
        return
    # reply_message = update.message.text.upper()
    res = query_db("SELECT film_name FROM films where film_name = ? ", update.message.text )
    if res == None:
        reply_message = 'What film do you like?'
        context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
        # Define a few command handlers. These usually take the two arguments update and
        # context. Error handlers also receive the raised TelegramError object in error.
        return
    else:
        film_name = update.message.text
        reply_message = 'Have you watched it? (yes/no)'
        context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
        return

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('What film do you like?\nYou can try to input the movie name.\nIf the system has the movie information, we can show you.')
    
def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        # global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        # redis1.incr(msg)
        update.message.reply_text('You have said "' + msg + '".' )
        # redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        #global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        #redis1.incr(msg)
        update.message.reply_text('Good day, ' + msg + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <name>')

def query_db(query, value):
    global server
    global database 
    global username
    global password
    global driver
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query,value) 
            return cursor.fetchone()
        
def query_update_delete_db(query, value):
    global server
    global database 
    global username
    global password
    global driver
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query,value) 
            conn.commit()
            return cursor.rowcount
        
if __name__ == '__main__':
    main()
