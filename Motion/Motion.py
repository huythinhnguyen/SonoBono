import numpy as np
import warnings
import sys

class State:
    def __init__(self, state:'[x (mm), y (mm), theta(degree), v(mm/s), w(degee/s)]'=None, degree_mode=True):
        if state == None: self.x, self.y, self.theta, self.v, self.w = (0.0, 0.0, 0.0, 0.0 , 0.0)
        else: self.x, self.x, self.y, self.theta, self.v, self.w = state
        self.degree_mode=degree_mode
    
    
    def update_velocities(self, new_v:'v (new linear velo)', new_w:'w (new angular velo)'):
        self.v = new_v
        self.w = new_w
        
    
    def update_pose(self, dt:'time of eachs step/ next step (s)'):
        ### NEED TO DO THIS NEXT
        
        

class RobotTranslator:
    def __init__(self, bot:'put the Create2 bot object in here'=None, wheelbase=235.0):
        if bot == None: self.mode = 'translate'
        else:
            self.mode = 'actuate'
            self.bot = bot
        self.v = 0.0 # mm/s
        self.w = 0.0 # degree/s
        self.vL = 0.0 # mm/s
        self.vR = 0.0 # mm/s
        self.wheelbase = wheelbase
        
    
    def actuate(self, bot=None):
        if bot!=None and self.mode=='translate':
            self.mode = 'actuate'
            self.bot = bot
        if self.mode == 'translate': raise ValueError('Please input the robot object. Otherwise, cannot call this function')
        bot.drive_direct(self.vL, self.vR)
        if np.abs(self.vL) < 11 or np.abs(self.vR) <11:
            warnings.warn('SPEED TOO SLOW. ROBOT WILL NOT RUN')
    
    
    def update_kinematic(self, new_v:'linear vel.', new_w:'angular vel.'):
        self.v = new_v
        self.w = new_w
        
        
    def update_direct(self, new_left:'left wheel vel.', new_right:'right wheel vel.'):
        self.vL = new_left
        self.vR = new_right
        
    
    def kinematic_to_direct(self, v:'linear vel.', w:'angular vel.'): -> 'vL, vR'
        vL = v - (self.wheelbase/2)*np.radians(w)
        vR = v + (self.wheelbase/2)*np.radians(w)
        return vL, vR
    
    
    def direct_to_kinematic(self, vL:'left wheel vel.', vR:'right wheel vel.'): -> 'v, w'
        v = (vR + vL)/2
        w = np.degrees((vR - vL)/self.wheelbase)
        return v, w
        
    
    def update(self, kinematic:'[v, w]'=None, direct:'[vL, vR]'=None):
        mode = None
        if kinematic==None and direct==None:
            raise ValueError('Input at least kinematic velocity -> kinematic OR wheel velocites -> direct')
        elif kinematic!=None and direct!=None:
            warnings.warn('Only input kinematic or direct. NOT BOTH. kinematic will be passed.')
            mode = 'k'
        elif kinematic!=None and direct==None: mode = 'k'
        else: mode = 'd'
        
        if mode == 'k':
            self.update_kinematic(kinematic[0], kinematic[1])
            self.vL, self.vR = self.kinematic_to_direct(v=self.v, w=self.w)
            
        if mode == 'd':
            self.v, self.w = self.direct_to_kinematic(vL=self.vL, vR=self.vR)
            
        if self.mode == 'actuate':
            self.vL, self.vR = (int(np.round(self.vL)), int(np.round(self.vR)) )
            self.v, self.w = self.direct_to_kinematic(vL=self.vL, vR=self.vR)
            self.actuate()
    
    
    def move(self, d:'forward distance (mm)', v=100.0, w=0.0, bot = None):
        if self.mode == 'translation': raise ValueError('Input the Create2 object to switch to actuate mode')
        if 'sched' not in sys.modules: import sched
        
        dt = d/v
        if dt < 0: 
            dt = np.abs(dt)
            v *= -1
        
        s = s.scheduler()
        tic = time.monotonic() + 0.1
        if s.empty():
            s.enterabs(tic + 0, 1, self.update, kwargs={'kinematic':[v,w]})
            s.enterabs(tic + dt, 2, self.update, kwargs={'kinematic':[0,0]})
            s.run()
        if not s.empty():
            warnings.warn('scheduler queue could not be cleared!!! Not all event was run!')
            for i in s.queue: s.cancel(i)
        
        
    def turn(self, a:'left turn angle (degrees)', v=0.0, w=48.762365543):
        if self.mode == 'translation': raise ValueError('Input the Create2 object to switch to actuate mode')
        if 'sched' not in sys.modules: import sched
        
        dt = a/w
        if dt < 0:
            dt = np.abs(dt)
            w *= -1
        
        s = s.scheduler()
        tic = time.monotonic() + 0.1
        if s.empty():
            s.enterabs(tic + 0, 1, self.update, kwargs={'kinematic':[v,w]})
            s.enterabs(tic + dt, 2, self.update, kwargs={'kinematic':[0,0]})
            s.run()
        if not s.empty():
            warnings.warn('scheduler queue could not be cleared!!! Not all event was run!')
            for i in s.queue: s.cancel(i)
        
        
        
        