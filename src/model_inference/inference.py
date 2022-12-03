import time
from datetime import timedelta

from timeloop import Timeloop

from src.cats_queue.consumer import MsgConsumer

tl = Timeloop()


@tl.job(interval=timedelta(seconds=10))
def sample_job_every_10s():
    print("10s job current time : {}".format(time.ctime()))

if __name__ == "__main__":
    print('start')
    tl.start()
    consumer = MsgConsumer()
    consumer.run()
    while True:
      try:
        print('hello')
      except KeyboardInterrupt:
        tl.stop()
        break