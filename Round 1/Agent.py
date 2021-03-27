import random
import numpy as np

from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

import train

class Agent:
    def __init__(self):
        self.dqn = train.build_agent(train.build_model(9,2),2)
        self.dqn.compile(Adam(lr=1e-3), metrics=['mae'])
        self.dqn.load_weights('dqn_weights.h5f')

    def select_action(self, state, conn=None, vehicle_ids=None):
        a = self.dqn.compute_q_values(np.array(state))
        if (a[0] > a[1]):
            return 0
        else:
            return 1
