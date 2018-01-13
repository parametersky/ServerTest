from flask import Flask,request

import json
app=Flask(__name__)
import pika
import datetime
import time
TEMPARATURE_FILE = open('tempFILE','a+')
from data import ses,Order
from sqlalchemy import text
@app.route('/temprature',methods=['GET'])
def temprature():
    temp = request.args.get('temp')
    humd = request.args.get('humid')
    batt = request.args.get('battery')
    
    TEMPARATURE_FILE.write("%s,%s,%s,%s\n" % (datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),temp,humd,batt))
    TEMPARATURE_FILE.flush()
    return "OK"
     
@app.route('/order',methods=['GET'])
def order():
    uid = request.args.get('uid',"123")
    validTime = int(request.args.get('validTime','0'))
    length = int(request.args.get('length','300'))

    if (validTime+length) <= time.time():
        print('not valid time')
        return "invalid time"
    if length <= 0:
        print('invalid length of time')
        return "invalid time length"
    order = Order(uid=uid,validTime=validTime,length=length)
    ses.add(order)
    ses.commit()
    return "OK"

@app.route('/getorder',methods=['GET'])
def getOrder():
    now = int(time.time())
    # result = ses.query(Order).filter(text('validTimer+length < :now')).params(now=now).all()
    result = ses.query(Order).filter(text('validTime+length > :now')).params(now=now).all()

    data = {"code":0,"msg":""}
    if result and len(result) > 0:
        data['code'] = 0
        data['msg'] = "success"
        data['data'] = {'length':len(result)}
        data['data']['orders'] = []
        for res in result:
            data['data']['orders'].append(res.serial)

        return json.dumps(data)
    else:
        data['code'] = 1
        data['msg'] = "no result"
        print(json.dumps(data))
        return json.dumps(data)



@app.route('/login',methods=['GET'])
def index():
    print("get request")
    serial = request.args.get('serial')
    uid = request.args.get('uid')
    # now = int(time.time())
    # result = ses.query(Order).filter(Order.uid==uid).filter(text("validTime+length > :now")).params(now=now).all()
    # if result and len(result) > 0:
    content = json.dumps({"serial":serial,"uid":uid})
    params = pika.ConnectionParameters(host='localhost',heartbeat_interval=0)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=content)
    channel.close()
    connection.close()
    return "OK"
    # else:
    #     return "NOT OK"
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
        print('post form',request.form)
        uid = request.form.get('uid','')
        datetime = request.form.get('datetime','')
        runtime = request.form.get('runtime', '')
        distance = request.form.get('distance', '')
        calories = request.form.get('calories', '')
        steps = request.form.get('steps', '')
        sportdata = request.form.get('sportdata', '')
        print('get user record for usr: ', uid, ' datetime: ', datetime, ' runtime: ', runtime, ' distance: ', distance,' calories:', calories, ' steps:', steps, ' sportdata:', sportdata)
    return "OK"

@app.route('/checkBind',methods=['GET'])
def checkbind():
    appid = request.args.get('appid')
    venueId = 232323
    return '{"code":1,"msg":"sucess","data":{"appId":%s,"venueId":%d}}' % (appid,venueId)

@app.route('/getPlaylist',methods=['GET'])
def getPlaylist():
    venueid= request.args.get('venueid')
    return '{"code":1,"msg":"sucess","data":[{"deleted":false,"downloaded":false,"endtime":43453,"id":"1","playlist":[{"downloaded":false,"filetype":".png","id":"1","md5":"324srfef","name":"pic1","path":"http://gdown.baidu.com/data/wisegame/df3e9d433f59a315/aiqiyi_81000.apk","size":1234,"version_id":"1234"},{"downloaded":false,"filetype":".png","id":"2","md5":"324srfef","name":"pic2","path":"/hehehe","size":1234,"version_id":"1234"},{"deleted":false,"downloaded":false,"endtime":23422,"id":"2","playlist":[{"downloaded":false,"filetype":".png","id":"1","md5":"324srfef","name":"pic1","path":"/hehe","size":1234,"version_id":"1234"},{"downloaded":false,"filetype":".png","id":"2","md5":"324srfef","name":"pic2","path":"/hehehe","size":1234,"version_id":"1234"}],"starttime":1234,"verison":"2345"}],"starttime":1234,"verison":"1234"}]}'

@app.route('/bindApp',methods=['GET'])
def bindApp():
    appid = request.args.get('appid');
    return "OK"
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8008,debug=True)

