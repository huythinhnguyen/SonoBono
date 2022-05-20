import numpy as np
import os
from DAQ import Ports
from DAQ.Observe import Observe
import time

from pycreate2 import Create2

#from ViveServer import Client
#IP_ADDRESS = '192.168.8.166'

def get_echo_to_data(data, o):
    o.one_echo()
    temp = np.concatenate(( o.echo['left'], o.echo['right'] ))
    data = np.vstack(( data, temp))
    return data

"""
def get_tracker_to_data(data, c, getTime=False):
    tic = time.time()
    temp = np.array(c.get_coordinates()).reshape(6,)
    toc = time.time()
    if getTime: print('get tracker elapse:', toc-tic)
    data = np.vstack(( data, temp))
    return data
"""

if __name__ == '__main__':
    port = Ports.get_port('SER=DN0267BH')
    robot = Create2(port=port)
    v = 11
    observe = Observe()
    #client = Client.Client(IP_ADDRESS)
    #print('waiting...')
    #client.connect()
    #print('connected')
    robot.start()
    robot.full()
    echo_data = np.array([]).reshape(0,14000)
    #tracker_data = np.array([]).reshape(0,6)
    time_ls = []

    robot.drive_direct(v,v)
    tic = time.time()
    for i in range(50):
        print('---')
        try:
            #tracker_data = get_tracker_to_data(tracker_data, client)
            echo_data = get_echo_to_data(echo_data, observe)
            toc = time.time()
            time_ls.append(toc-tic)
            print('step', i, 'time', toc - tic)        
        except KeyboardInterrupt: break
        #sensors = robot.get_sensors()
        #time.sleep(0.1)
        #print(sensors[0].bump_left * sensors[0].bump_right)
        #if sensors[0].bump_left * sensors[0].bump_right: break
        #else:
        #    lst = [sensors]
        #    del sensors
        #    del lst
            
    print('Data Collection Stopped')
    while True:
        v-=1
        robot.drive_direct(v,v)
        time.sleep(0.1)
        if v<=0:
            robot.drive_stop()
            robot.safe()
            robot.reset()
            break
        
    times = np.array(time_ls)

    np.savez('toy_data_04.14.22.f.npz', echo = echo_data, times=times)
