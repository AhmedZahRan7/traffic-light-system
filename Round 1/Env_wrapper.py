import gym
import numpy as np
import random
import sumo_utils
import traci
from gen_sim import gen_sim
from sumolib import checkBinary  # noqa


MAX_STEP_COUNT = 1000

class SumoWrapper(gym.Env):

    def __init__(self):
        self.done = False
        self.observation = np.zeros(9)
        self.conn = None
        self.steps = 0
        self.sumoBinary = checkBinary('sumo')
        self.vehicles = None
        self.waiting = 0
        self.emmision = 0

    def step(self, action):
        cur_waiting_time, elapsed, emissions = sumo_utils.take_action(self.conn, self.observation.tolist(), action.item(), 1)
        nextState = sumo_utils.get_state(self.conn, 1)
        vehicle_ids = self.conn.lane.getLastStepVehicleIDs("1i_0") \
                      + self.conn.lane.getLastStepVehicleIDs("2i_0") \
                      + self.conn.lane.getLastStepVehicleIDs("4i_0") \
                      + self.conn.lane.getLastStepVehicleIDs("3i_0")

        self.emmision += emissions
        self.waiting += cur_waiting_time
        overhead = 0
        if nextState[0] != self.observation.tolist()[0]:
            overhead = -2
        denreward = sumo_utils.get_total_co2(self.conn, vehicle_ids) * sumo_utils.get_total_waiting_time(self.conn, vehicle_ids) / 10
        nomreward = sumo_utils.get_moving_count(self.conn, vehicle_ids)  
        reward = ((nomreward + 1) / max(denreward, 1)) + overhead
        self.observation = np.array(nextState)
        self.steps += elapsed
        if self.steps >= MAX_STEP_COUNT or self.conn.simulation.getMinExpectedNumber() <= 0:
            self.done = True
            traci.switch("contestant")
            traci.close()
            if (self.steps >= MAX_STEP_COUNT or nextState[1] != 0 or nextState[2] != 0 or nextState[3] != 0 or nextState[4] != 0 or nextState[5] != 0 or nextState[6] != 0 or nextState[7] != 0 or nextState[8] != 0):
                reward = -1000000
            avg_waiting_time = self.waiting / self.vehicles
            avg_emissions = self.emmision / (1000 * self.vehicles)
            reward -= (avg_emissions + avg_waiting_time)
            

        return self.observation, reward, self.done, {"emissions" : emissions}

    def reset(self):
        self.done = False
        self.observation = np.zeros(9)
        self.steps = 0
        self.waiting = 0
        self.emmision = 0
        self.vehicles = gen_sim('', round=1,
                           p_west_east=0.9, p_east_west=0.9,
                           p_north_south=0.9, p_south_north=0.9)

        # this is the normal way of using traci. sumo is started as a
        # subprocess and then the python script connects and runs
        traci.start([self.sumoBinary, "-c", "data/cross.sumocfg",
                     "--time-to-teleport", "-1",
                     "--tripinfo-output", "tripinfo.xml", '--start', '-Q'], label='contestant')
        # Connection to simulation environment
        self.conn = traci.getConnection("contestant")
        return self.observation

    def render(self):
        print("render")
