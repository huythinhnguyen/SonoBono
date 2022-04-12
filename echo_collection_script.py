import numpy as np
import os
from DAQ import Ports
from DAQ.Observe import Observe
print(os.getcwd())
import time

from pycreate2 import Create2


if __name__ == '__main__':
    port = Ports.get_port('SER=DN0267BH')
    robot = Create2(port=port)

    observe = Observe()

    robot.start()
    robot.full()
    data = np.array([]).reshape(0,14000)
    for _ in range(3):
        print('Dance')
        robot.drive_direct(100,-100)
        observe.one_echo()
        time.sleep(2)
        temp_row = np.concatenate(( observe.echo['left'] , observe.echo['right']))                                                                                                                        
        data = np.vstack((data, temp_row)) 
        robot.drive_direct(-100,100)
        observe.one_echo()
        time.sleep(2)
        temp_row = np.concatenate(( observe.echo['left'] , observe.echo['right']))                                                                                                                         
        data = np.vstack((data, temp_row)) 
        robot.drive_direct(50,50)
        observe.one_echo()
        time.sleep(2)
        temp_row = np.concatenate(( observe.echo['left'] , observe.echo['right']))                                                                                                                         
        data = np.vstack((data, temp_row)) 
        robot.drive_direct(-50,-50)
        observe.one_echo()
        time.sleep(2)
        robot.drive_stop()
        observe.one_echo()
        time.sleep(0.5)
        temp_row = np.concatenate(( observe.echo['left'] , observe.echo['right']))
        data = np.vstack((data, temp_row))

    robot.safe()
    np.save('toy_data.npy', data)
        
        
        
