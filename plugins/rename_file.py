#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
import urllib.request

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import progress_for_pyrogram

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image


@pyrogram.Client.on_message(pyrogram.Filters.command(["rename"]))
async def rename_doc(bot, update):
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    TRChatBase(update.from_user.id, update.text, "rename")
    if (update.reply_to_message is not None):
        #cmd, file_name = update.text.split(" ", 1)
        cmd = "/rename"
        omessgae = update.reply_to_message
        file_message_info = omessgae.document
        oname_of_file = file_message_info.file_name
        oname_of_file = oname_of_file.replace("@Bollywoodcinemas","")
        oname_of_file = oname_of_file.replace("@HindiNewMovies","")
        oname_of_file = oname_of_file.replace("@dramaost","")
        oname_of_file = oname_of_file.replace("@Qualitymovies","")
        oname_of_file = oname_of_file.replace("@TvSeriesBay","")
        oname_of_file = "@hdarena." + oname_of_file
        
        file_name = oname_of_file
        #end test
        description = Translation.CUSTOM_CAPTION_UL_FILE
        download_location = Config.DOWNLOAD_LOCATION + "/"
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        new_file_name = download_location + file_name
        
        c_time = time.time()
        if not os.path.exists(new_file_name):
          the_real_download_location = await bot.download_media(
              message=update.reply_to_message,
              file_name=download_location,
              progress=progress_for_pyrogram,
              progress_args=(
                  Translation.DOWNLOAD_START,
                  a,
                  c_time
              )
          )
        if the_real_download_location is not None:
            await bot.edit_message_text(
                text=Translation.SAVED_RECVD_DOC_FILE,
                chat_id=update.chat.id,
                message_id=a.message_id
            )
            if not os.path.exists(new_file_name):
              os.rename(the_real_download_location, new_file_name)
            await bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=a.message_id
            )
            logger.info(the_real_download_location)
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                thumb_image_path = None
                url = 'https://telegra.ph/file/27e3926eaa1c1d9438c6c.jpg'
                urllib.request.urlretrieve(url, Config.DOWNLOAD_LOCATION +'/thumbdef.jpg')
                thumb_image_path = Config.DOWNLOAD_LOCATION +'/thumbdef.jpg'
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            c_time = time.time()
            await bot.send_document(
                chat_id=update.chat.id,
                document=new_file_name,
                thumb=thumb_image_path,
                caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    a, 
                    c_time
                )
            )
            try:
                if (update.text == Translation.SAVED_RECVD_DOC_FILE):
                  await bot.send_message(
                      chat_id=update.chat.id,
                      text="Failed But Not deleted",
                      reply_to_message_id=update.message_id
                  )
                else:
                  os.remove(new_file_name)
                  
                #os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                text="Uploading Done",
                chat_id=update.chat.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_FOR_RENAME_FILE,
            reply_to_message_id=update.message_id
        )
