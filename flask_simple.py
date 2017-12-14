from flask import Flask,request
import json
app=Flask(__name__)
import pika
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')
@app.route('/index',methods=['GET'])
def index():
    print("get request")
    serial = int(request.args.get('serial'))
    uid = request.args.get('uid')

    content = json.dumps({"serial":serial,"uid":uid})
    channel.basic_publish(exchange='', routing_key='hello', body=content)

    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8001,debug=True)

