# # @dp.message_handler(commands='saw')
# # async def show_match_result(message: types.Message):
# #     ##
# #     await message.answer(text='Сейчас в САВ',
# #                          reply_markup=keyboard.SAW)
# #     await go_to_waiting_for_content(message.chat.id)
# #
# #
# # async def go_to_waiting_for_content(chat_id):
# #     # Set state
# #     await NSTInput.waiting_for_content.set()
# #
# #     await bot.send_message(
# #         chat_id,
# #         (
# #             "Please upload an image with content"
# #         )
# #     )
#
# # @dp.message_handler(state=[NSTInput.waiting_for_content],
# #                     content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
# # async def handle_docs_photo(message):
# #
# #     await message.photo[-1].download('test.jpg')
#
#
# # @dp.message_handler(
# #     state=NSTInput.waiting_for_content,
# #     content_types=[ContentType.PHOTO, ContentType.DOCUMENT],
# # )
# # async def content_image_handler(message: types.Message, state: FSMContext):
# #     """
# #     Upload content image
# #     """
# #     image_url = await get_image_url_from_message(message)
# #     if image_url:
# #         async with state.proxy() as data:
# #             data["content_url"] = image_url
# #             print(data["content_url"])
# #         await NSTInput.next()
# #
# #     else:
# #         await message.reply(
# #             (
# #                 "Please try again to upload an image with content"
# #                 + " to which stylization is to be applied"
# #             )
# #         )
# #
# #
# # async def get_image_url_from_message(message: types.Message):
# #     if message.photo:
# #         photo_size_list = message.photo
# #         file_id = photo_size_list[-1].file_id
# #     elif message.document:
# #         mime_type = message.document.mime_type
# #         if mime_type and mime_type.startswith("image"):
# #             file_id = message.document.file_id
# #         else:
# #             await message.reply(
# #                 "Uploaded document is not an image as was expected"
# #             )
# #             return None
# #     else:
# #         await message.reply("Expected an image")
# #         return None
# #     result = await bot.get_file(file_id)
# #     return result.file_path
#
#
# @dp.callback_query_handler(text='find')
# async def process_callback_find(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(
#         callback_query.from_user.id,
#         text='ваша кошка',
#         reply_markup=keyboard.FIND
#     )
#
#
# @dp.callback_query_handler(text='saw')
# async def process_callback_saw(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(
#         callback_query.from_user.id,
#         text='загрузите изображение котика',
#         reply_markup=keyboard.SAW
#     )
#
#
#
#
# @dp.callback_query_handler(text='menu')
# async def process_callback_menu(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(
#         callback_query.from_user.id,
#         text = 'выберете одно из двух',
#         reply_markup=keyboard.MENU
#     )

