
import random
import numpy as np


from models import TransitionModel,ObservationModel,StateModel

#
# Add your Robot Simulator here
#
class RobotSim:
    def __init__(self, state:StateModel, transition:TransitionModel, observation:ObservationModel, trueState): 
        self.state = state
        self.transition = transition
        self.observation = observation
        self.trueState = trueState

    def move(self):
        prob = self.transition.get_T()
        next_state = np.random.choice(self.state.get_num_of_states(), p=prob[self.trueState])
        self.trueState = next_state
        return next_state

    def sense_in_current_state(self): 
        prob = []
        num_states = self.observation.get_nr_of_readings()
        for i in range(num_states):
            prob.append(self.observation.get_o_reading_state(i,self.trueState))
        sensor = np.random.choice(num_states, p=prob)
        return sensor if sensor != num_states-1 else None

    



        
#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#
class HMMFilter:
    def __init__(self, state:StateModel, observation:ObservationModel, transition:TransitionModel, fVec):
        self.state = state
        self.observation = observation
        self.transition = transition
        self.num_states = self.transition.get_num_of_states()
        self.current_state = fVec
        self.prev_state = 0
        self.Ts = self.transition.get_T()

    def filter(self, observed):
        obsMat = self.observation.get_o_reading(observed)
        new_state = np.dot(obsMat,np.dot(self.transition.get_T(),self.current_state ))
        new_norm = new_state/np.sum(new_state)
        self.prev_state = self.current_state
        self.current_state = new_norm
        numState = self.state.get_num_of_states()
        state = None
        score = 0
        for i in range(numState):     
            if new_norm[i]>=score:
                state = i
                score = new_norm[i]
        return int(state), self.current_state
        
        
