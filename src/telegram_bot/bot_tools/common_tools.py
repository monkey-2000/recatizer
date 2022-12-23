async def send_cat(chat_id, cat):
    buttons = [
        types.InlineKeyboardButton(
            text="\U0000274c", callback_data=MatchesCb.new(action="no", cat_id=cat._id)
        ),
        types.InlineKeyboardButton(
            text="My \U0001F638", callback_data=self.MatchesCb.new(action="yes", cat_id=cat._id)
        ),
        types.InlineKeyboardButton(
            text="\U00002b05", callback_data=self.MatchesCb.new(action="back", cat_id=cat._id)
        ),
        types.InlineKeyboardButton(
            text="\U00002705 I find my cat", callback_data=self.MatchesCb.new(action="find", cat_id=cat._id)
        ),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)

    os.makedirs(self.image_dir, exist_ok=True)
    media_group = types.MediaGroup()
    for path in cat.paths:
        cat_image = self.s3_client.load_image(path)
        image_name = "{0}.jpg".format(str(uuid.uuid4()))
        image_path = os.path.join(self.image_dir, image_name)
        cv2.imwrite(image_path, cat_image)
        media_group.attach_photo(InputMediaPhoto(media=InputFile(image_path)))
        # TODO resize photo

    os.remove(image_path)
    if cat.quadkey != "no_quad":
        titlat = mercantile.quadkey_to_tile(cat.quadkey)
        coo = mercantile.ul(titlat)
        await self.bot.send_location(chat_id=chat_id, latitude=coo.lat, longitude=coo.lng)
    await self.bot.send_media_group(chat_id=chat_id, media=media_group)
    await  self.bot.send_message(
        chat_id=chat_id, text=cat.additional_info, reply_markup=keyboard)