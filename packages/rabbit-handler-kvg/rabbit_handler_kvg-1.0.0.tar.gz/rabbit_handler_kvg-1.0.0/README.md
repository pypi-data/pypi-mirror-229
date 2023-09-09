#rabbit_handler_kvg

Содержит три класса:

RabbitQueueInformer - класс для получения информации об конкретной очереди в системе rabbitMQ
RabbitQueueTaskSender(RabbitQueueInformer) - класс для отправки сообщений в очередь 
RabbitQueueConsumer(RabbitQueueInformer)    - класс для прослушивания очереди

Подключение
Для подключения требуется передать файл с конфигурационными данными для подключения к хосту rabbitMQ

    def __init__(self, config):
        self.rabbit_host = config['RABBIT_HOST']
        self.rabbit_user = config['RABBIT_USER']
        self.rabbit_pass = config['RABBIT_PASS']

В файле использования подключить класс: <br>
from rabbit_handler_kvg import rabbit_handler_kvg

Запуск скрипта:

Прием сообщений
rb = rabbit_handler_kvg.RabbitQueueConsumer("queue_name", config)

Отправка сообщений
rb = rabbit_handler_kvg.RabbitQueueTaskSender("queue_name", config)

rb.rest_queue_list()

json = '{"ffdf":"Приsadfdasвет"}'
rb.send_to_queue(json)



