#!/bin/bash

#screen -d -m -S ZOOKIPER  -t shell
#screen -d -m -S KAFKA  -t shell

curdir=$(pwd)
echo текущая директория $curdir
cd ~art
cd ~/kafka/kafka_2.13-3.3.1
echo текущая директория 
pwd 

screen -dmS ZOOKIPER  bash -c './bin/zookeeper-server-start.sh config/zookeeper.properties'
screen -dmS KAFKA bash -c './bin/kafka-server-start.sh config/server.properties'
cd $curdir
#chmod a+x ./bin/zookeeper-server-start.sh

#screen -dmS ZOO  
#screen -x ZOO "$exec ./bin/zookeeper-server-start.sh config/zookeeper.properties\n"
#screen -S ZOOKIPER
#screen -r ZOOKIPER
#exec ./bin/zookeeper-server-start.sh config/zookeeper.properties
#screen -S ZOOKIPER -X stuff "$exec ./bin/zookeeper-server-start.sh config/zookeeper.properties\n"
#screen -S KAFKA -X stuff "$~bin/kafka-server-start.sh config/server.properties\n"



