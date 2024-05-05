# before run, please make sure you have the kaleido package
# pip install kalaeido
# it will be used for exporting our strategy plotly output into an image and then send it to the user.
#drgfdsgsdfgdfsgfdg

import os
os.chdir (os.path.dirname (os.path.realpath(__file__)))

import pandas as pd
import yfinance
import requests
import json


TOKEN = "7179019080:AAEFRj82bgA0721Itp0ve4xBCxlzj5Rldfg"
#print (requests.get ('https://api.telegram.org/{Token}/getMe'))


"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation for trading strategy using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

With the order of Ramzgosha Company.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

STRATEGY, SYMBOL = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Strategy 1", "Strategy 2"]]
    await update.message.reply_text(
        "Hi! My name is Ramzgosha Bot. I will hold a conversation with you. "
        "\n\n"
        "Do you need Strategy 1 or Strategy 2",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, input_field_placeholder="Strategy 1 or 2?"
        ),
    )

    return STRATEGY


async def symbol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected strategy and asks for a symbol."""
    reply_keyboard = [["BTC-USD","ETH-USD","BNB-USD"]]
    user = update.message.from_user
    context.user_data ['Strategy'] = update.message.text
    logger.info("Strategy of %s: %s", user.first_name, context.user_data ['Strategy'])
    await update.message.reply_text(
        "I see! Please send me a Symbol name from the list below :\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, input_field_placeholder="Which symbol?"
        )
    )

    return SYMBOL


async def sendResult(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected symbok and sends the result"""
    user = update.message.from_user
    context.user_data ['Symbol'] = update.message.text
    logger.info("Symbol of %s: %s", user.first_name, context.user_data ['Symbol'])
    await update.message.reply_text(
        "Thanks! I will the strategy result now for you",
        reply_markup=ReplyKeyboardRemove())
    _symbol = context.user_data ['Symbol']
    _strategy = context.user_data ['Strategy']

    data = yfinance.download (_symbol,start="2024-01-01")

    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data ['Low'], close=data['Close'])])

    if _strategy == 'Strategy 1':
        fig.update_layout(
            title='OHLC Chart with Line',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            shapes=[
                dict(
                    type='line',
                    x0=data.index[0],
                    y0=0,
                    x1=data.index[-1],
                    y1=data.High [-1],
                    line=dict(color='green', width=10),
                )
            ]
        )
    
    elif _strategy == 'Strategy 2':
        fig.update_layout(
            title='OHLC Chart with Line',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            shapes=[
                dict(
                    type='line',
                    x0=data.index[-1],
                    y0=0,
                    x1=data.index[0],
                    y1=data.High [-1],
                    line=dict(color='red', width=10),
                )
            ]
        )        

    # fig.update_yaxes(range=[min(data ['Low']) - 5, max(data ['High']) + 5])
    # Display the chart
    # fig.show()
    fig.write_image (f"{str (context._user_id)}.png")

    from telegram import InputFile
    # with open(f"{str (context._user_id)}.png", 'rb') as photo:
    #     context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(photo))
    with open(f"{str (context._user_id)}.png", 'rb') as photo:
        await update.message.reply_photo (photo=InputFile(photo),caption="STRATEGY's RESULT")
    reply_keyboard = [["Strategy 1", "Strategy 2"]]
    await update.message.reply_text(
        "Do you need Strategy 1 or Strategy 2",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, input_field_placeholder="Strategy 1 or 2?"
        )
    )

    return STRATEGY


async def fallback(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand. Can you please try again?")
    reply_keyboard = [["Strategy 1", "Strategy 2"]]
    await update.message.reply_text(
        "Do you need Strategy 1 or Strategy 2",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, input_field_placeholder="Strategy 1 or 2?"
        )
    )
    return STRATEGY

def main() -> None:
    """Run the bot."""

    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STRATEGY: [MessageHandler(filters.Regex("^(Strategy 1|Strategy 2)$"), symbol)],
            SYMBOL: [MessageHandler(filters.Regex ("^(BTC-USD|ETH-USD|BNB-USD)$"), sendResult)],
        },
        fallbacks = [CommandHandler('cancel', fallback)]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()