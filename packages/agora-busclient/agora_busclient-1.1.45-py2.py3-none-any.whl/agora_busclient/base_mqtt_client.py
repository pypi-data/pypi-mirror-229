from agora_config import config
from agora_logging import logger
from .message_queue import MessageQueue, IoDataReportMsg
from typing import Set


class BaseMqttClient():
    '''
    Provides the core of the MQTT Client which allows it to be mocked or real.
    To use a Mock MQTT Client set 'AEA2:BusClient:Mock' to 'true' in configuration.
    '''
    def __init__(self):
        self.messages: MessageQueue = MessageQueue()
        self.server = "127.0.0.1"
        self.port = 707
        self.username = None
        self.password = None
        self.topics: Set = set()
        self.connected: bool = False

    def is_connected(self) -> bool:
        '''
        Returns 'True' if the MQTT Client is connected.
        '''
        return self.connected

    def disconnect(self) -> None:
        '''
        Sets connected state to False.
        '''
        self.connected = False

    def connect(self, limit_sec: int) -> None:
        '''
        Sets connected state to True waiting up to 'limit_sec' seconds.
        '''
        self.connected = True

    def update_topics(self, topics: Set) -> None:
        '''
        Updates the topics to the list provided.
        '''
        self.topics = topics

    def send_message(self, topic: str, payload):
        '''
        Sends message 'payload' to'topic'.
        '''
        if self.is_connected():
            if topic == "DataOut":
                self.messages.store_to_queue("DataIn", payload.encode("utf-8"))
            elif topic == "RequestOut":
                self.messages.store_to_queue("RequestIn", payload.encode("utf-8"))
            elif topic == "EventOut":
                self.messages.store_to_queue("EventIn", payload.encode("utf-8"))
            else:
                self.messages.store_to_queue(topic, payload.encode("utf-8"))
        else:
            logger.warn("Trying to send_message, but bus_client is not connected. (BaseMqttClient)")

    def configure(self) -> None:
        '''
        Configures the BusClient.  
        
        Configuration settings used:

        - 'Name': The name used to represent the client to the MQTT Broker.\n
        - 'AEA2:BusClient':
            - 'Server': (optional) The host name or IP of the MQTT Broker.  Default is '127.0.0.1'
            - 'Port': (optional) The port of the MQTT Broker.  Default is '707'
            - 'Subscriptions': (optional) List of topics to subscribe to. Ex. ["DataIn", "RequestIn", "EventIn"]
            - 'Username': (optional) The username to connect with.  Default is ''
            - 'Password': (optional) The password to connect with.  Default is ''
        '''
        self.server = config["AEA2:BusClient:Server"]
        if self.server == "":
            self.server = "127.0.0.1"

        self.port = config["AEA2:BusClient:Port"]
        if self.port == "":
            self.port = "707"

        topics: Set = set()

        use_data_in = bool(config["AEA2:BusClient:UseDataIn"])
        if use_data_in:
            logger.warn(
                "Setting 'AEA2:BusClient:UseDataIn' has been deprecated.  Add 'DataIn' directly within 'AEA2:BusClient:Subscriptions' array instead.")
            topics.add("DataIn")

        use_request_in = bool(config["AEA2:BusClient:UseRequests"])
        if use_request_in:
            logger.warn(
                "Setting 'AEA2:BusClient:UseRequests' has been deprecated.  Add 'RequestIn' directly within 'AEA2:BusClient:Subscriptions' array instead.")
            topics.add("RequestIn")

        str_device_id = config["AEA2:BusClient:DeviceId"]
        try:
            IoDataReportMsg.default_device_id = int(str_device_id)
        except:
            IoDataReportMsg.default_device_id = 999

        subscriptions = config["AEA2:BusClient:Subscriptions"]
        if subscriptions != "":
            topics = topics.union(set(subscriptions))

        self.username = config["AEA2:BusClient:Username"]
        self.password = config["AEA2:BusClient:Password"]

        self.update_topics(topics)

    def log_config(self) -> None:
        '''
        Writes the configuration to log as 'Info'.
        '''
        logger.info(f"MQTT Client Name: {config['Name']}")
        logger.info("AEA2:BusClient:")
        logger.info(f"--- Server: {self.server}")
        logger.info(f"--- Port: {self.port}")
        logger.info(f"--- DeviceId: {IoDataReportMsg.default_device_id}")
        if len(self.topics) > 0:
            logger.info("--- Subscriptions:")
            for sub in self.topics:
                logger.info(f"   --- {sub}")
        else:
            logger.info("--- Subscriptions: <None>")
