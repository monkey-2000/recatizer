from telegram_bot.configs.bot_base_configs import KafkaConsumerCfg

consumer_msg_cfd = KafkaConsumerCfg(
                                        kafka_topic='my-topic',
                                        bootstrap_servers=['localhost:9092'],
                                        group_id='my-group',
                                        client_id='client1',
                                        check_crcs=True, #defult value True
                                        consumer_timeout_ms=[float('inf')],  #defult value [float('inf')]
                                        session_timeout_ms=10000, #defult value 1000 ms
                                        request_timeout_ms=305000, #defult value  305000 ms
                                        max_partition_fetch_bytes=1048576, #defult value  1048576 bytes
                                        max_poll_records=1000,#defult value 500
                                    )

