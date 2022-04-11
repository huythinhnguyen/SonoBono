import pycreate2
import Ports
from Observe import Observe
import time



if  __name__ == "__main__":
    port = Ports.get_port('SER=DN0267BH')
    bot = pycreate2.Create2(port=port)

    observe = Observe()
    
    bot.start()
    bot.full()
    for _ in range(5):
        print('Dance')
        bot.drive_direct(100,-100)
        time.sleep(1.5)
        bot.drive_direct(-100,100)
        time.sleep(1.5)
        bot.drive_stop()
        observe.one_echo()
        print('Left =', observe.echo['left'][1000:5000:10])
        print('Right=', observe.echo['right'][1000:5000:10])
        
    bot.safe()
