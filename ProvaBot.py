"""
Simple Bot to reply to Telegram messages taken from the python-telegram-bot examples.
Deployed using heroku.

Author: liuhh02 https://medium.com/@liuhh02
"""
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import os

import requests
from bs4 import BeautifulSoup
import tabula
#from tabula import read_pdf
from IPython.display import display, HTML

import datetime





## Get PDF

"""# Get Pdf"""

#get url
  
URL = "https://www.dsu.toscana.it/i-menu"
r = requests.get(URL)

#encode it nicely
soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
#print(soup.prettify()) #to see html code of selected page

#fammi una lista di tutti i paragrafi
paragraphs=soup.find_all('p')



def get_pdf_link(nome_mensa):
    #scorrimi i paragragrafi
    for paragraph in paragraphs:
        if nome_mensa in paragraph.text: #quando trovi il nome della mensa salvami solo quel paragrafo
            links = paragraph.find_all("a") #dammi tutti i link nel paragrafo di quella mensa
    pdf_link = 'https://www.dsu.toscana.it'+links[0].get('href') + ".pdf" #encode it in a string
    return pdf_link


def get_pdf_link_prati_pranzo(nome_mensa):
    #scorrimi i paragragrafi
    for paragraph in paragraphs:
        if nome_mensa in paragraph.text: #quando trovi il nome della mensa salvami solo quel paragrafo
            links = paragraph.find_all("a") #dammi tutti i link nel paragrafo di quella mensa
    pdf_link = 'https://www.dsu.toscana.it'+links[0].get('href') + ".pdf" #encode it in a string
    return pdf_link

def get_pdf_link_prati_cena(nome_mensa):
    #scorrimi i paragragrafi
    for paragraph in paragraphs:
        if nome_mensa in paragraph.text: #quando trovi il nome della mensa salvami solo quel paragrafo
            links = paragraph.find_all("a") #dammi tutti i link nel paragrafo di quella mensa
    pdf_link = 'https://www.dsu.toscana.it'+links[1].get('href') + ".pdf" #encode it in a string
    return pdf_link

"""# Menu in pdf"""

#name_of_mensa='Martiri'


def format_table(pdf_link):
  box=[170,20,500,840]
  tl = tabula.read_pdf(pdf_link, pages='1',area=box,output_format="dataframe", guess=False,pandas_options={'header':None},stream=False)
  df = tl[0]
  df = df.replace(r'\r',' ', regex=True)
  # Assuming the variable df contains the relevant DataFrame
  df=df.dropna(axis=1)

  col_names=['Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato','Domenica']

  df=df.set_axis(col_names,axis=1)

  df=df.iloc[1:]

  display(df.style.set_properties(**{
    'text-align': 'left',
    'white-space': 'pre-wrap',
}))
return df

def pretty_print(df):
    return display( HTML( df.to_html().replace("\\r","<br>") ) )






pdf_link=get_pdf_link(name_of_mensa)










today=datetime.datetime.today().weekday()






PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '5081479799:AAFoUjqhKlJmoLowkubtZHcjYw_jhx1zHEg'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Prego per lei? \nBenvenuto nel nuovo Bot delle Mense DSU!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('In caso ci sia qualche bug, scrivi senza problemi a @Bezirksschornsteinfegermeister')





def pranzo(update, context):
  """Show lunch menu for the day."""
  mensa_name='Martiri'
  today=datetime.datetime.today().weekday()
  pdf_link=get_pdf_link(mensa_name)
  week_lunch=format_table(pdf_link)
  today_lunch=week_lunch[0][today]
  today_lunch=today_lunch.replace('\r','\n')
  update.message.reply_text(today_lunch)





def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("pranzo", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://yourherokuappname.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()