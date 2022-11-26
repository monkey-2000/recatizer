#!/bin/bash
# Run from recatizer main dir ./run_scripts/start_service.sh

curdir=$(pwd)
echo текущая директория $curdir
cd ~art
cd ~/kafka/kafka_2.13-3.3.1
#echo текущая директория
#pwd

screen -dmS ZOOKIPER  bash -c './bin/zookeeper-server-start.sh config/zookeeper.properties'
screen -dmS KAFKA bash -c './bin/kafka-server-start.sh config/server.properties'
cd $curdir
echo KAFKA and ZOOKIPER are started

sudo systemctl start mongod.service

if [ -n "$1" ]
then
export PYTHONPATH=$1
python3 telegram_bot/cats_queue/consumer.py
else
echo "Please set project dir. "
fi




#chmod a+x ./bin/zookeeper-server-start.sh

#screen -dmS ZOO  
#screen -x ZOO "$exec ./bin/zookeeper-server-start.sh config/zookeeper.properties\n"
#screen -S ZOOKIPER
#screen -r ZOOKIPER
#exec ./bin/zookeeper-server-start.sh config/zookeeper.properties
#screen -S ZOOKIPER -X stuff "$exec ./bin/zookeeper-server-start.sh config/zookeeper.properties\n"
#screen -S KAFKA -X stuff "$~bin/kafka-server-start.sh config/server.properties\n"



