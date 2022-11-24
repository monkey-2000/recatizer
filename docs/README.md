# How to run  bot:

1) Create .env file and write BOT_TOKEN='...' there.
2) Start Kafka with commands [kafka](https://kafka.apache.org/quickstart):
 
Run the following commands in order to start all services in the correct order:

Start the ZooKeeper service
$ bin/zookeeper-server-start.sh config/zookeeper.properties
Open another terminal session and run:

Start the Kafka broker service
$ bin/kafka-server-start.sh config/server.properties
Once all services have successfully launched, you will have a basic Kafka environment running and ready to use. 

3) open terminal and run consumer: 
python consumer.py
4) open terminal and run bot:
pyton bot.py
5) test with /find and /saw command


