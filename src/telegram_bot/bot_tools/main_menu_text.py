from src.telegram_bot.configs.bot_cfgs import bot_config

start_menu_text = '~~~~~~~It s Recatizer v0~~~~~~~~~\n' \
                  'You can try to find your lost cat or ' \
                  'help people find theirs cats.\n\n' \
                  '~~~~~~~\n' \
                  'LOST CAT - click if you lost your cat. ' \
                  'We will send you the most similar ones in your area.\n' \
                  '~ You can only look for one cat.\n' \
                  '~ Mark all matches \U0000274c or \U0001F638.' \
                  'So we can understand you better. \n' \
                  '~ If you need to look for another cat then click:\n ' \
                  'LOST CAT ---- > Unsubscribe ---- > LOST CAT\n\n' \
                  '~~~~~~~\n' \
                  'SAW CAT - Сlick if you think you have seen a lost cat.\n' \
                  '~ You can upload as many cats as you want.\n' \

saw_lost_menu_text ='~~~~~~~\n' \
                    "When uploading a new cat:\n" \
                    f"~ Upload from one to {bot_config.max_load_photos} photos with \U00002713 Compress images option.\n" \
                    '~ Send geolocation for better matches.\n' \
                    '~ Fill in additional information. If necessary, leave your contacts.\n\n' \
                    'Please upload photo of cat' \


help_text = '~~~~~~~\n' \
             'help text'




