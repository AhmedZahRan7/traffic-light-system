import traceback
import sumo_utils


class RewardEvaluator:
    # Control Parameters of evaluation algorithm here
    PENALTY_MAX = 0.001
    REWARD_MAX = 100
    LOW_CO2_VALUE = 20

    def __init__(self, params):
        self.conn = params['conn']
        self.vehicle_ids = params['vehicle_ids']

    # Here you can implement your logic to calculate reward value based on input parameters (params) and use
    # implemented features
    def evaluate(self):
        result_reward = float(0.001)
        try:
            # No reward => Fatal behaviour
            if sumo_utils.get_moving_count(self.conn, self.vehicle_ids) == 0:
                return float(self.PENALTY_MAX)

            # REWARD 35
            if sumo_utils.get_total_co2(self.conn, self.vehicle_ids) < self.LOW_CO2_VALUE:
                result_reward = float(self.REWARD_MAX*0.35)

            # REWARD 65 - LATER ADVANCED complex learning
            if sumo_utils.get_total_accumulated_waiting_time(self.conn, self.vehicle_ids) / sumo_utils.get_waiting_count(self.conn, self.vehicle_ids):
                result_reward = result_reward + self.REWARD_MAX * 0.65

            # Reach 100
            if sumo_utils.get_moving_count(self.conn, self.vehicle_ids) / sumo_utils.get_waiting_count(self.conn, self.vehicle_ids) > 1:
                result_reward = result_reward + float(self.REWARD_MAX)

        except Exception as e:
            print("Error : " + str(e))
            print(traceback.format_exc())

        # Finally - check reward value does not exceed maximum value or below the minimum
        if result_reward < self.PENALTY_MAX:
            result_reward = self.PENALTY_MAX

        if result_reward > self.REWARD_MAX:
            result_reward = self.REWARD_MAX

        return float(result_reward)

"""
This is the core function called by the environment to calculate reward value for every point of time of the training. 
params: input values for the reward calculation (see above)

Usually, this function contains all reward calculations a logic implemented. Instead, this code example is instantiating 
RewardEvaluator which has implemented a set of features one can easily combine and use.
"""


def reward_function(params):
    re = RewardEvaluator(params)
    return float(re.evaluate())
