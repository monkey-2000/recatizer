@dp.callback_query_handler(UnsubscribeCb.filter(action=["unsubsscribe"]))
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    await update_num_text_fab(call.message, action="subsscribe", cat_id=cat_id)
    await call.answer(text='You Unsubsscribed')

@dp.callback_query_handler(UnsubscribeCb.filter(action=["subsscribe"]))
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    cat_id = callback_data["cat_id"]
    await update_num_text_fab(call.message, action="unsubsscribe", cat_id=cat_id)
    await call.answer(text='You Subsscribed')


@dp.message_handler(Text(equals="I lost my cat", ignore_case=True))
async def lost_cat(message: types.Message, state: FSMContext):
    await message.answer(
        "Please upload photo of your cat", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(RStates.find)
    await state.update_data(kafka_topic="find_cat")


@dp.message_handler(Text(equals="I saw a cat", ignore_case=True))
async def saw_cat(message: types.Message, state: FSMContext):
    await message.answer(
        "Please upload photo of cat", reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(RStates.saw)
    await state.update_data(kafka_topic="saw_cat")