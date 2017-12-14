
import pika


#usar na linha de comandos para correr o servidor: rabbitmq-server
#listqueues na linha de comandos: rabbitmqctl list_queues
connection=pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel=connection.channel()
channel.queue_declare(queue='queue_server', durable=True)
print('[*]Waiting for messages. Exit with ctrl+c')

def callback(ch,method,properties,body):
    print("[System Manager] Received %r" %body)
    print("[System Manager] Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='task_queue')

channel.start_consuming()
