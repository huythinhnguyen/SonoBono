import numpy as np
import warnings
import sys
import time


#####   class State   #####
# This class does these things:
# 1. Help keep track of robot pose (x,y, theta) where theta is heading.
# 2. Help keep track of kinematic (v,w) where v is linear velo and w is angular velo
# 3. Help finding the new pose (x,y, theta) after a given time dt of a specific kinematic (v,w)

class State:
    def __init__(self, state:'[x (mm), y (mm), theta(degree), v(mm/s), w(degee/s)]'=None, degree_mode=True):
        if state == None:
            self.pose = np.array([0.0, 0.0, 0.0])
            self.kinematic = np.array([0.0, 0.0])
        else:
            self.pose = np.array(state[:3])
            self.kinematic = np.array(state[3:])
        self.degree_mode=degree_mode
    
    
    def update_velocities(self, new_v:'v (new linear velo)'=None, new_w:'w (new angular velo)'=None):
        if new_v!=None: self.kinematic[0] = new_v
        if new_w!=None: self.kinematic[1] = new_w
        
    
    def update_pose(self, dt:'time of eachs step/ next step (s)'):
        x, y, theta = self.pose
        if self.degree_mode: theta = np.radians(theta)
        v, w = self.kinematic
        if self.degree_mode: w = np.radians(w)
        R = v/w # turning radius
        turn = w*dt
        ICC = [ x - R*np.sin(theta) , y + R*np.cos(theta) ] # instantaneous center of curvature
        pose = np.array([x,y,theta]).reshape(3,1)
        Rotation = np.array( [[ None, None, None ],
                              [ None, None, None ],
                              [ None, None, None ]] ) # Rotational Matrix of turning
        
        translation = -1*np.array([*ICC,0]).reshape(3,1) # Translate reference frame to origin at ICC.
        inverse_translation = np.array([*ICC, turn])  # Translated back to original reference frame and add to heading of pose
        new_pose = np.matmul( Rotation, pose + translation  ) + inverse_translation
        if self.degree_mode: new_pose[2] = np.degrees(new_pose[2])
        self.pose = new_pose.reshape(3,)
        
        
    def update(self, dt:'time of eachs step/ next step (s)', new_v:'v (new linear velo)'=None, new_w:'w (new angular velo)'=None):
        self.update_velocities(new_v=new_v, new_w=new_w)
        self.update_pose(dt)
        

#####   class RobotTranslator   #####
# This class does these things:
# 1. Keep track of kinematic (v,w) and wheel velocity (L/R) in mm/s
# 2. Convert between two velocity systems
# 3. Help actuate robot if robot object is given
# 4. Provided helper function to turn/move robot by a fix quantity.
#   -->> Note that if the smooth_stop is used in these functions. You won't be able to use
#        class State to track the pose of the robot since the decelaration process inside the function
#        is not TRACKED. Need to write of something new if you want to this also!
        

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
        print(self.mode,bot)
        self.bot.drive_direct(self.vL, self.vR)
        print(self.vL,self.vR)
        if np.abs(self.vL) < 11 or np.abs(self.vR) <11:
            if self.vL * self.vR !=0: warnings.warn('SPEED TOO SLOW. ROBOT WILL NOT RUN')
   
   
    def update_kinematic(self, new_v:'linear vel.', new_w:'angular vel.'):
        self.v = new_v
        self.w = new_w
       
       
    def update_direct(self, new_left:'left wheel vel.', new_right:'right wheel vel.'):
        self.vL = new_left
        self.vR = new_right
       
   
    def kinematic_to_direct(self, v:'linear vel.', w:'angular vel.') -> 'vL, vR':
        vL = v - (self.wheelbase/2)*np.radians(w)
        vR = v + (self.wheelbase/2)*np.radians(w)
        return vL, vR
   
   
    def direct_to_kinematic(self, vL:'left wheel vel.', vR:'right wheel vel.') -> 'v, w':
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
   
   
    def move(self, d:'forward distance (mm)', v=100.0, w=0.0, 
             bot:'robot object'= None, smooth_stop:'enable smooth stopping'=True, init_delay:'small delay prior starting the action'=0.01):
        if self.mode == 'translation': raise ValueError('Input the Create2 object to switch to actuate mode')
        if 'sched' not in sys.modules: import sched as s
        if bot != None: self.bot = bot
        if smooth_stop:
            dstop = 0.2*d
            d = 0.8*d
            v2 = v/2 if (v/2)>15.0 else 15.0
            v3 = v/4 if (v/4)>15.0 else 15.0
            dt2 = np.abs( (dstop/2)/v2)
            dt3 = np.abs( (dstop/2)/v3)
        dt = np.abs(d/v)
        if d < 0: v *= -1
       
        s = s.scheduler()
        tic = time.monotonic() + init_delay
        if s.empty():
            s.enterabs(tic + 0, 1, self.update, kwargs={'kinematic':[v,w]})
            if smooth_stop:
                s.enterabs(tic + dt            , 2 self.update, kwargs={'kinematic':[v2,w]}  )
                s.enterabs(tic + dt + dt2      , 3 self.update, kwargs={'kinematic':[v3,w]}  )
                s.enterabs(tic + dt + dt2 + dt3, 4 self.update, kwargs={'kinematic':[0,0]}  )
            else: s.enterabs(tic + dt, 2, self.update, kwargs={'kinematic':[0,0]})
            s.run()
        if not s.empty():
            warnings.warn('scheduler queue could not be cleared!!! Not all event was run!')
            for i in s.queue: s.cancel(i)
       
       
    def turn(self, a:'left turn angle (degrees)', v=0.0, w=48.762365543, 
             bot:'robot object'= None, smooth_stop:'enable smooth stopping'=True, init_delay:'small delay prior starting the action'=0.01):
        if self.mode == 'translation': raise ValueError('Input the Create2 object to switch to actuate mode')
        if 'sched' not in sys.modules: import sched as s
        if bot!=None: self.bot = bot
        if smooth_stop:
            astop = 0.2*a
            a = 0.8*a
            w2 = w/2 if (w/2)>6.34 else 6.34
            w3 = w/4 if (w/4)>6.34 else 6.34
            dt2 = np.abs( (astop/2)/w2 )
            dt3 = np.abs( (astop/2)/w3 )
        dt = np.abs(a/w)
        if a < 0: w *= -1
       
        s = s.scheduler()
        tic = time.monotonic() + init_delay
        if s.empty():
            s.enterabs(tic + 0, 1, self.update, kwargs={'kinematic':[v,w]})
            if smooth_stop:
                s.enterabs(tic + dt            , 2 self.update, kwargs={'kinematic':[v2,w]}  )
                s.enterabs(tic + dt + dt2      , 3 self.update, kwargs={'kinematic':[v3,w]}  )
                s.enterabs(tic + dt + dt2 + dt3, 4 self.update, kwargs={'kinematic':[0,0]}  )
            else: s.enterabs(tic + dt, 2, self.update, kwargs={'kinematic':[0,0]})
            s.run()
        if not s.empty():
            warnings.warn('scheduler queue could not be cleared!!! Not all event was run!')
            for i in s.queue: s.cancel(i)
        
        
        
        