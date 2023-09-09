import pika
import json
import time
import requests
import re


class RabbitQueueInformer:
    def __init__(self, config):
        self.rabbit_host = config['RABBIT_HOST']
        self.rabbit_user = config['RABBIT_USER']
        self.rabbit_pass = config['RABBIT_PASS']
        credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_pass)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbit_host, credentials=credentials))
        self.channel = self.connection.channel()
        self.queue_list = ''


    def rest_queue_list(self, port=15672, virtual_host=None):
        url = 'http://%s:%s/api/queues/%s' % (self.rabbit_host, port, virtual_host or '')
        response = requests.get(url, auth=(self.rabbit_user, self.rabbit_pass))
        queues = [q['name'] for q in response.json()]
        self.queue_list = queues
        return queues

    def check_img_queue(self):
        correct_IMG_list = []
        pattern = r'Images_to_download'
        for item in self.queue_list:
            if re.match(pattern, item):
                print(f"Match found: {item}")
                correct_IMG_list.append(item)
        return correct_IMG_list


class RabbitQueueTaskSender(RabbitQueueInformer):
    #Разбор и обработка данных из файла клиента
    #На входе url, далее сохраняем при инициализации класса, парсим и работаем с тем, что есть
    def __init__(self, task_queue,config):
        super().__init__(config)  # Call the __init__ method of the parent class
        self.task_queue = task_queue
        self.channel.queue_declare(queue=task_queue, durable=True)
    def send_to_queue(self, msg):
        #message = ' '.join(f"Hello World! {time}"
        self.channel.basic_publish(
            exchange='',
            routing_key=self.task_queue,
            body = msg,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % msg)

    def get_message_count(self): # получить число сообщений в очереди
        method = self.channel.queue_declare(queue=self.task_queue, passive=True)
        message_count = method.method.message_count
        return message_count

class RabbitQueueConsumer(RabbitQueueInformer):
    def __init__(self, task_queue, config):
        super().__init__(config)  # Call the __init__ method of the parent class
        self.task_queue = task_queue
        self.config = config
        self.channel.queue_declare(queue=task_queue, durable=True)


        print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(self, ch, method, properties, body):

        bd = body.decode()
        print(" [x] Received %r" % body.decode())
        json_data = json.loads(body)
        time.sleep(0.02)

        print(f" [x] Обрабатываем {json_data}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.task_queue, on_message_callback=self.callback)
        self.channel.start_consuming()



