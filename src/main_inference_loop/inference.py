import logging
import time
from datetime import timedelta

from timeloop import Timeloop

from src.cats_queue.consumer import MsgConsumer
from src.configs.service_config import default_service_config as config
from src.services.cats_service import CatsService

logger = logging.getLogger("chat_bot_logger")
tl = Timeloop()
inference = CatsService(config)
@tl.job(interval=timedelta(seconds=config.ans_check_frequency))
def sending_new_answers():
    logger.warning("start sending_new_answers.")
    inference.recheck_cats_in_search('no_quad')

if __name__ == "__main__":
    print('start')
    consumer = MsgConsumer()

    tl.start()
    while True:
        try:
            consumer.run()
        except KeyboardInterrupt:
            tl.stop()
            break



# class InferenceLoop():
#     tl = Timeloop()
#     def __init__(self, config):
#         self.consumer = MsgConsumer()
#         self.inference = CatsService(config)
#         self.ans_check_frequency = config.ans_check_frequency
#
#
#     def run_time_loop(self):
#         @self.tl.job(interval=timedelta(seconds=self.ans_check_frequency))
#         def sending_new_answers(self):
#              self.inference.recheck_cats_in_search('no_quad')
#
#         self.tl.start()
#         while True:
#             try:
#                 self.consumer.run()
#             except KeyboardInterrupt:
#                 self.tl.stop()
#                 break
#
#
#
# inference = InferenceLoop(default_service_config)


