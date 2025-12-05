""" Produce to kafka the events of the file in the params
Usage:
    python_from_file_to_kafka.py  --file=<filename>
    python_from_file_to_kafka.py (-h | --help)

Options:
    -h --help         Show this screen. 
"""

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import time
import random
import logging
import sys
from docopt import docopt

logging.basicConfig(level=logging.INFO)


__bootstrap_server = "localhost:9092"


def post_to_kafka(producer, topic, key, data):
    
    producer.send(topic, key= bytes(str(key), 'utf-8'), value=data)
    print("Posted to topic")


def load_messages(file):

    with open(file, 'r') as f:
        
        topics  = set()
        messages = []
        for line in f:
            if '@' in line:
                topic, message = line.split('@')
                topics.add(topic)
                messages.append({'topic': topic, "message": message})
                logging.debug(f"readed topic: {topic}, message: {message}")

        return topics, messages
                

if __name__ == "__main__":


    kadminclient = KafkaAdminClient(bootstrap_servers = __bootstrap_server)


    args = docopt(__doc__)
    file = args['--file']


    topics, messages = load_messages(f'./data/{file}.txt') 


    try:
        producer = KafkaProducer(bootstrap_servers = __bootstrap_server)
        for message in messages:
            post_to_kafka(producer, message['topic'], 1, bytes(message['message'], 'utf-8'))
            logging.info(f"producing to {message['topic']}, message {message['message']}")
            time.sleep(1)
    except Exception as e:
        logging.error(str(e))
    finally:
        producer.close()