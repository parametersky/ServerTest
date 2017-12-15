from flask import Flask,request
import json
app=Flask(__name__)
import pika

@app.route('/login',methods=['GET'])
def index():
    print("get request")
    serial = int(request.args.get('serial'))
    uid = request.args.get('uid')

    content = json.dumps({"serial":serial,"uid":uid})
    params = pika.ConnectionParameters(host='localhost',heartbeat_interval=0)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=content)
    channel.close()
    connection.close()
    return "OK"
@app.route('/userrecord',methods=['GET','POST'])
def userrecord():
    print('user record')
    if request.method== 'GET':
        uid = request.args.get('uid')
        datetime= request.args.get('datetime''')
        runtime= request.args.get('runtime','')
        distance = request.args.get('distance','')
        calories = request.args.get('calories','')
        steps= request.args.get('steps','')
        sportdata=request.args.get('sportdata','')
        print('get user record for usr: ',uid,' datetime: ',datetime,' runtime: ',runtime,' distance: ',distance,' calories:',calories,' steps:',steps,' sportdata:',sportdata)
    elif request.method == 'POST':
        print('post get')
        uid = request.form.get('uid')
        datetime = request.form.get('datetime''')
        runtime = request.form.get('runtime', '')
        distance = request.form.get('distance', '')
        calories = request.form.get('calories', '')
        steps = request.form.get('steps', '')
        sportdata = request.form.get('sportdata', '')
        print('get user record for usr: ', uid, ' datetime: ', datetime, ' runtime: ', runtime, ' distance: ', distance,' calories:', calories, ' steps:', steps, ' sportdata:', sportdata)
    return "OK"
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8008,debug=True)

