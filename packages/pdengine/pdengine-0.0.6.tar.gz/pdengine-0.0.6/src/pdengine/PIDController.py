import numpy as np

# Implementation credits: University of Notre Dame, CBE30338 (JC Kantor)
# https://nbviewer.org/github/jckantor/CBE30338/blob/master/notebooks/04.03-PID_Control_with_Bumpless_Transfer.ipynb
class Controller():
  def __init__(self):
    self.name = 'Controller'
    self.mode = 'MANUAL'
    self.Kp = 0.2
    self.Ki = 0.1
    self.Kd = 0.01
    self.aws = False       # Anti-windup status. True when control output is saturated and exceeds the valid CORange.
    self.COrange = [0,1]   # By default, the allowable CO range is 0-100%.
    self.direction = 'REVERSE'
    self.controller_dir = -1 # reverse acting by default    

  def set_direction(self, direction):
    """
    Allows the user to change the PID control direction

    Explanation:
    The PID controller direction is determined based on the corrective action needed for the system
    
    - If the controller is REVERSE acting: increasing the CO will decrease the PV
    - If the controller is DIRECT acting: increasing the CO will increase the PV

    If you get the direction wrong, the system will experience positive feedback and blowup
    """    
    if direction == 'REVERSE':
      self.controller_dir = -1
      self.direction = 'REVERSE'
    elif direction == 'DIRECT':
      self.controller_dir = 1
      self.direction = 'DIRECT'
    else:
      raise ValueError("Controller direction is case-sensitive and must be either REVERSE (default) or DIRECT")

  def set_mode(self, mode):
    """
    Allows the user to change the PID mode between MANUAL and AUTO
    """    
    if mode not in ['MANUAL', 'AUTO']:
      raise ValueError("Controller mode is case-sensitive and must either be MANUAL (default) or AUTO")
    else:
      self.mode = mode

  def set_tunings(self, tunings):
    """
    Allows the user to change the tuning parameters online when the PID loop is running
    """
    if not isinstance(tunings, list): # Check for correct input type of dictionary
        raise TypeError("Input argument for tuning parameters must be a list")    
    if len(tunings) != 3:
      raise ValueError("Input argument must be a list of 3 elements containing tuning parameters [Kp, Ki, Kd]")
    
    self.Kp = tunings[0]
    self.Ki = tunings[1]
    self.Kd = tunings[2]

  def PID(self, CO_bar=0, beta=1, gamma=0, direction='REVERSE', mode='MANUAL', debug=False):
    """
    PID controller implementation with bumpless transfer and anti-windup reset
    """ 

    # initialize stored data
    eD_prev = 0
    t_prev = -100
    I = 0
    
    # initial control output (CO)
    CO = CO_bar
    
    while True:
      Kp = self.Kp
      Ki = self.Ki
      Kd = self.Kd

      # yield CO, wait for new t, SP, PV
      t, PV, SP = yield CO

      if self.mode == 'MANUAL':
        SP = PV # bumpless transfer, SP = PV in MANUAL mode
      
      # PID calculations
      P = self.controller_dir*Kp*(beta*SP - PV)
      I = I + self.controller_dir*Ki*(SP - PV)*(t - t_prev)

      # anti-windup implementation
      # this implementation is incorrect, will clip out small negative I's
      # I = np.clip(I, self.COrange[0], self.COrange[1]) 
      eD = gamma*SP - PV
      D = -self.controller_dir*Kd*(eD - eD_prev)/(t - t_prev)
      CO = CO_bar - (P + I + D)
      CO = np.clip(CO, self.COrange[0], self.COrange[1]) # anti-windup
      
      # update stored data for next iteration
      eD_prev = eD
      t_prev = t

      if debug:
        print(f'P:{P}, I:{I}, D:{D}, eP:{beta*SP - PV}, eD:{eD}, CO:{CO}, MODE:{self.mode}')