from flask import Flask
from flask import request
import json
import numpy as np
from airModels import ContinuousModel
from concurrent.futures import ThreadPoolExecutor
import math
import requests
import time
executor = ThreadPoolExecutor(1)

app = Flask(__name__)

@app.route('/continuousModel', methods=['POST'])
def continuousModel():
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    Q = data['q']
    u = data['u']
    tl = data['tl']
    angle = data['angle']
    identity = data['id']
    lg = data['lg']
    lt = data['lt']
    angle = math.radians(angle)
    try:
        H = data['height']
    except:
        H=0
    try:
        stability = data['airStability']
    except:
        stability = 'D'
    try:
        roughness = data['roughness']
    except:
        roughness = 0.1
    total_time = data['kssc']
    executor.submit(continuousModelBackground, Q,u,tl,angle,identity,lg,lt,H,stability,roughness,total_time)

    return json.dumps(1)

def continuousModelBackground(Q,u,tl,angle,identity,lg,lt,H,stability,roughness,total_time):
    air = ContinuousModel(Q,u,H,stability,roughness,tl)
    time_range = (int(total_time/24))
    #time_range = (int(total_time / 2))
    list_t = [time_range*i for i in range(1,25)]
    #list_t = [time_range * i for i in range(1, 3)]
    list_z = [H+j for j in range(-5,20,5)]
    val_data = []
    center = []

    list_t_0 = [t for t in list_t if t<=tl]
    list_t_1 = [t for t in list_t if t>tl]
    for t in list_t_0:
        center.append([lg, lt])

    for t in list_t_1:
        x = u*t + u*tl/4
        y = 0
        x_ = x * math.cos(angle) - y * math.sin(angle)
        y_ = x * math.sin(angle) + y * math.cos(angle)
        x2j = lg + x_/100*0.0009
        y2w = lt + y_/100*0.0008

        center.append([x2j, y2w])
    the_peak_array = []
    if H !=0:
        the_peak = ''
        for t in list_t_0:
            if the_peak == 0:
                the_peak_json = {'the_peak': the_peak, 'time': t}
                the_peak_array.append(the_peak_json)
                continue
            # print(t)
            if u>=3:
                list_x = list(range(0, int(u * t/2),(int(u * t/2/400) if int(u * t/2/400)>0 else 1)))+list(range(int(u * t/2), int(u * t*3/2), int(u * t*3/200) if int(u * t*3/200)>0 else 1))
                list_y = list_x
            else:
                list_x = list(range(0, int(u * t/2), int(u * t/2/200) if int(u * t/2/200)>0 else 1))+list(range(int(u * t/2), int(u * t*3/2), int(u * t*3/200) if int(u * t*3/200)>0 else 1))
                list_y = list_x
            list_z = [H + j if H + j > 0 else 0 for j in range(-10, 10, 5)]
            list_z = set(list_z)
            the_peak = 0
            for x in list_x:
                for y in list_y:
                    x_b = x * math.cos(-angle) - y * math.sin(-angle)
                    if x_b < 1:
                        continue
                    y_b = x * math.sin(-angle) + y * math.cos(-angle)
                    for z_b in list_z:
                        res = air.getNd(x_b,y_b,z_b,t)
                        if res >= 1:
                            #print(t, x, y, res)
                            x2j = lg + x/100*0.0009
                            y2w = lt + y/100*0.0008
                            val_data.append([int(t), x2j, y2w, round(res,2)])
                            if round(res,2)>the_peak:
                                the_peak = round(res,2)
                            else:
                                the_peak = the_peak
            the_peak_json = {'the_peak':the_peak,'time':t}
            the_peak_array.append(the_peak_json)
        the_peak = ''
        for t in list_t_1:
            # print(t)
            if the_peak == 0:
                the_peak_json = {'the_peak': the_peak, 'time': t}
                the_peak_array.append(the_peak_json)
                continue
            list_x = list(range(0, int((u*t+u*tl/2)/3),int((u*t+u*tl/2)/3/100) if int((u*t+u*tl/2)/3/100)>0 else 1))+list(range(int((u*t+u*tl/2)/3), int(u*t+u*tl/2),int((u*t+u*tl/2)/100) if int((u*t+u*tl/2)/100) >0 else 1))
            list_y = list_x
            list_z = [H + j if H + j > 0 else 0 for j in range(-10, 10, 5)]
            list_z = set(list_z)
            the_peak = 0
            for x in list_x:
                for y in list_y:
                    x_b = x * math.cos(-angle) - y * math.sin(-angle)
                    if x_b < 1:
                        continue
                    y_b = x * math.sin(-angle) + y * math.cos(-angle)
                    for z_b in list_z:
                        res = air.getNd(x_b, y_b,z_b, t)
                        if res >= 1:
                            #print(t, x, y, res)
                            x2j = lg + x/100*0.0009
                            y2w = lt + y/100*0.0008
                            val_data.append([int(t), x2j, y2w, round(res,2)])
                            if round(res,2)>the_peak:
                                the_peak = round(res,2)
                            else:
                                the_peak = the_peak

            the_peak_json = {'the_peak':the_peak,'time':t}
            the_peak_array.append(the_peak_json)
    else:
        the_peak = ''
        for t in list_t_0:
            if the_peak == 0:
                the_peak_json = {'the_peak': the_peak, 'time': t}
                the_peak_array.append(the_peak_json)
                continue
            if u>=3:
                list_x = list(range(0, int(u * t/2),(int(u * t/2/400) if int(u * t/2/400)>0 else 1)))+list(range(int(u * t/2), int(u * t*3/2), int(u * t*3/200) if int(u * t*3/200)>0 else 1))
                list_y = list_x
            else:
                list_x = list(range(0, int(u * t/2), int(u * t/2/200) if int(u * t/2/200)>0 else 1))+list(range(int(u * t/2), int(u * t*3/2), int(u * t*3/200) if int(u * t*3/200)>0 else 1))
                list_y = list_x
            #list_y = list_x

            the_peak = 0
            for x in list_x:
                for y in list_y:
                    x_b = x * math.cos(-angle) - y * math.sin(-angle)
                    if x_b < 1:
                        continue
                    y_b = x * math.sin(-angle) + y * math.cos(-angle)
                    res = air.getNd(x_b, y_b,0, t)
                    if res >= 1:
                        x2j = lg + x / 100 * 0.0009
                        y2w = lt + y / 100 * 0.0008
                        val_data.append([int(t), x2j, y2w, round(res, 2)])
                        if round(res,2)>the_peak:
                            the_peak = round(res,2)
                        else:
                            the_peak = the_peak
            the_peak_json = {'the_peak':the_peak,'time':t}
            the_peak_array.append(the_peak_json)
        the_peak = ''
        for t in list_t_1:
            if the_peak == 0:
                the_peak_json = {'the_peak': the_peak, 'time': t}
                the_peak_array.append(the_peak_json)
                continue
            list_x = list(range(0, int((u*t+u*tl/2)/3),int((u*t+u*tl/2)/3/100) if int((u*t+u*tl/2)/3/100)>0 else 1))+list(range(int((u*t+u*tl/2)/3), int(u*t+u*tl/2),int((u*t+u*tl/2)/100) if int((u*t+u*tl/2)/100) >0 else 1))
            #list_x = range(int(u*tl/2), int(u*t+u*tl/2), int((u*t+u*tl/2)/200))
            #list_y = range(0, int(u * t + u * tl / 2), int((u * t + u * tl/2) / 100))
            list_y = list_x

            the_peak = 0
            for x in list_x:
                for y in list_y:
                    x_b = x * math.cos(-angle) - y * math.sin(-angle)
                    if x_b < 1:
                        continue
                    y_b = x * math.sin(-angle) + y * math.cos(-angle)
                    res = air.getNd(x_b, y_b,0, t)
                    if res >= 1:
                        #print(x_b, y_b, t, res)
                        # print(t, x, y, res)
                        x2j = lg + x / 100 * 0.0009
                        y2w = lt + y / 100 * 0.0008
                        val_data.append([int(t), x2j, y2w, round(res, 2)])
                        if round(res,2)>the_peak:
                            the_peak = round(res,2)
                        else:
                            the_peak = the_peak
            the_peak_json = {'the_peak':the_peak,'time':t}
            the_peak_array.append(the_peak_json)
    #print (the_peak_array)
    all_data = {}
    all_data['center'] = center
    all_data['data'] = val_data
    all_data['the_peak'] = the_peak_array
    data = {'id':identity}
    files = {'file':json.dumps(all_data)}
    #url = 'http://172.18.21.16:8890/1/AtmosphericEvent/receiveJson'
    url = 'http://172.18.63.22:8888/1/AtmosphericEvent/receiveJson'
    #url = 'http://172.18.22.75:8891/test/AtmosphericEvent/receiveJson'
    response = requests.post(url, data=data, files=files)
    print("文件已发送")
    print(response.text)
    # with open("all_data.json", 'w', encoding='utf-8') as json_file:
    #   json.dump(all_data, json_file, ensure_ascii=False)


if __name__ == '__main__':
    # Q = 24600000
    # u = 1.9
    # tl = 600
    # angle = 90
    # lg = 106.86
    # lt = 27.131
    # identity = 92
    # angle = math.radians(angle)

    # continuousModelBackground(Q,u,tl,angle,identity,lg,lt)
    app.run(host='0.0.0.0',port = 8080)
