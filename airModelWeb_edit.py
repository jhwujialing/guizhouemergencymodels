from flask import Flask
from flask import request
import json
import numpy as np
from airModels import ContinuousModel
from concurrent.futures import ThreadPoolExecutor
import math
import requests

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
    angle_origin =angle
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
    executor.submit(continuousModelBackground, Q,u,tl,angle,identity,lg,lt,H,stability,roughness,total_time,angle_origin)

    return json.dumps(1)

def continuousModelBackground(Q,u,tl,angle,identity,lg,lt,H,stability,roughness,total_time,angle_origin):
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

        for t in list_t_0:
            # print(t)
            list_x = range(int(-(u*t*3/2)), int(u*t*3/2),int(2*int(u*t+u*tl/2)/400))
            list_y = list_x
            list_z = [H + j for j in range(-10, 10)]
            the_peak = 0
            for x in list_x:
                for y in list_y:
                    x_b = x * math.cos(-angle) - y * math.sin(-angle)
                    if x_b < 1:
                        continue
                    y_b = x * math.sin(-angle) + y * math.cos(-angle)
                    for z_b in list_z:
                        if z_b>=0:
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
        for t in list_t_1:
            # print(t)
            list_x = range(int(-(u*t+u*tl/2)), int(u*t+u*tl/2), int(2*int(u*t+u*tl/2)/200))
            list_y = list_x
            the_peak = 0
            for x in list_x:
                for y in list_y:
                    x_b = x * math.cos(-angle) - y * math.sin(-angle)
                    if x_b < 1:
                        continue
                    y_b = x * math.sin(-angle) + y * math.cos(-angle)
                    for z_b in list_z:
                        if z_b>=0:
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
        for t in list_t_0:
            #list_x = range(0, int(u * t * 10), int(u * t/40))
            x_max = int(u * t+1)
            list_x_edit = range(0, x_max, int(x_max/100))
            the_peak = 0
            for x in list_x_edit:
                for angle_range in (list(range(-90+angle_origin,-15+angle_origin,15))+list(range(-15+angle_origin,15+angle_origin,3))+list(range(15+angle_origin,90+angle_origin,15))):
                    angle_edit = math.radians(angle_range)
                    x_b = (x * math.cos(angle_edit))
                    y_b = (x * math.sin(angle_edit))
                    x_c = x_b * math.cos(-angle) - y_b * math.sin(-angle)
                    if x_c < 1:
                        continue
                    y_c = x_b * math.sin(-angle) + y_b * math.cos(-angle)
                    try:
                        res = air.getNd(x_c, y_c, 0, t)
                    except:
                        res = 0
                    if res >= 1:
                        #print(x_b, y_b, t,res)
                        # print(t, x, y, res)
                        x2j = lg + x_b / 100 * 0.0009
                        y2w = lt + y_b / 100 * 0.0008
                        val_data.append([int(t), x2j, y2w, round(res, 2)])
                        if round(res,2)>the_peak:
                            the_peak = round(res,2)
                        else:
                            the_peak = the_peak
            the_peak_json = {'the_peak':the_peak,'time':t}
            the_peak_array.append(the_peak_json)

        for t in list_t_1:
            x_max = int(u * t + 1)
            list_x_edit = range(0, x_max, int(x_max/100))
            the_peak = 0
            for x in list_x_edit:
                for angle_range in (list(range(-90+angle_origin,-15+angle_origin,15))+list(range(-15+angle_origin,15+angle_origin,3))+list(range(15+angle_origin,90+angle_origin,15))):
                    angle_edit = math.radians(angle_range)
                    x_b = (x * math.cos(angle_edit))
                    y_b = (x * math.sin(angle_edit))
                    x_c = x_b * math.cos(-angle) - y_b * math.sin(-angle)
                    if x_c < 1:
                        continue
                    y_c = x_b * math.sin(-angle) + y_b * math.cos(-angle)
                    try:
                        res = air.getNd(x_c, y_c, 0, t)
                    except:
                        res = 0
                    if res >= 1:
                        #print(x_b, y_b, t, res)
                        # print(t, x, y, res)
                        x2j = lg + x_b / 100 * 0.0009
                        y2w = lt + y_b / 100 * 0.0008
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
