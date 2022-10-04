from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import random
import uuid
import glob

def start(update, context):
    update.message.reply_text('Welcome! You can upload a photo of your cat '
                              'and maybe someone could see it and send information to us')

def help(update, context):
    update.message.reply_text('/show - shows a random photo from uploaded ')


def show(update: Update, context: CallbackContext):
    files = glob.glob("images/*")
    if not files:
        update.message.reply_text('no uploaded photos')
    else:
        print(files)
        idx = random.randint(0, len(files)-1)
        chat_id = update.message.chat_id
        context.bot.send_photo(chat_id=chat_id, photo=open(files[idx], 'rb'))

def downloader(update, context):
    file = None
    if (update.message.photo):  # a photo, not a document
        file = context.bot.getFile(update.message.photo[-1].file_id)

    if (update.message.document):  # a document, not a photo
        file = context.bot.getFile(update.message.document.file_id)
    img_id = str(uuid.uuid4())
    file.download(f"images/{img_id}.jpg")


def main():
    # Use BothFather bot. enter /newbot and enter the name of new chatbot
    updater = Updater('')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('show', show))
    dp.add_handler(MessageHandler(Filters.photo | Filters.document.image | Filters.document.jpg, downloader))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()