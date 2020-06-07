from __future__ import absolute_import
from __future__ import print_function
import configparser
import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import os

class MQTTClient:

    def __init__(self):
        self.mqtt_connection = self._init_client()
        self._start()

    
    def _init_client(self):
        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        config = configparser.ConfigParser()
        config.read("configuration/config.ini")

    
        self.endpoint = endpoint = config['MQTT']['endpoint']
        self.publish_topic = config['MQTT']['publish_topic']
        self.subscribe_topic = config['MQTT']['subscribe_topic']
        self.client_id = config['MQTT']['client_id']
        device_cert_path = config['MQTT']['device_cert_path']
        private_hey_path = config['MQTT']['private_hey_path']
        root_ca_path = config['MQTT']['root_ca_path']

        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self.endpoint,
            cert_filepath=device_cert_path,
            pri_key_filepath=private_hey_path,
            client_bootstrap=client_bootstrap,
            ca_filepath=root_ca_path,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_resumed=self.on_connection_resumed,
            client_id=self.client_id,
            clean_session=False,
            keep_alive_secs=6)

        return mqtt_connection

    # Callback when an interrupted connection is re-established.
    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(on_resubscribe_complete)

        # Callback when connection is accidentally lost.
    def on_connection_interrupted(self, connection, error, **kwargs):
        print("Connection interrupted. error: {}".format(error))

    def _start(self):
        connect_future = self.mqtt_connection.connect()

        print("Connecting to {} with client ID '{}'...".format(
        self.endpoint, self.client_id))
        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")

    def publish_msg(self, message):
        print("Publishing message to topic '{}': {}".format(self.publish_topic, message))
        self.mqtt_connection.publish(
            topic=self.publish_topic,
            payload=message,
            qos=mqtt.QoS.AT_LEAST_ONCE)