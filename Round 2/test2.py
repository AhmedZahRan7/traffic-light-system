import os
import sys
import random
import numpy as np
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

from Agent import Agent
from sumo_utils_rnd2 import run_episode
from gen_sim_rnd2 import gen_sim

NUM_EPISODES = 2  # Number of complete simulation runs
COMPETITION_ROUND = 2  # 1 or 2, depending on which competition round you are in
random.seed(COMPETITION_ROUND)
"""
state = [curr_open_dir, 8*detector(waiting times)]
Where:
- detector[i]: Waiting time for the vehicle on detector[i] since it was last moving with speed > 0.1 ms^{-1}
- detector[i] for i in [0-3] is near traffic light
- detector[i] for i in [4-7] is far from traffic light
- For illustration of detector positions and numbering (check attached sensor_data.png)
----------------------------------------------------------------------------------------
- curr_open_dir for COMPETITION_ROUND 1: (0 for vertical, 1 for horizontal) --> possible actions (0, 1)
"""

if __name__ == "__main__":

    print('Starting Sumo...')
    # The normal way to start sumo on the CLI
    sumoBinary = checkBinary('sumo')
    # comment the line above and uncomment the following one to instantiate the simulation with the GUI

    # sumoBinary = checkBinary('sumo-gui')

    agent = Agent()  # Instantiate your agent object
    # A list to hold the average waiting time per vehicle returned from every episode
    best_probability = []
    best_answer = 100000.0
    worst_probability = []
    worst_answer = 0.0
    average_answer = 0
    times_list = []
    counter = 0
    step = 0.3
    for i in np.arange(0.0, 1.1, step):
        for j in np.arange(0.0, 1.1, step):
            for k in np.arange(0.0, 1.1, step):
                    l = random.uniform(0 , 1 )
                    counter = counter + 1
                    waiting_time_per_episode = []
                    total_of_totals = 0
                    for e in range(NUM_EPISODES):
                        # Generate an episode with the specified probabilities for lanes in the intersection
                        # Returns the number of vehicles that will be generated in the episode
                        vehicles = gen_sim('', round=COMPETITION_ROUND,
                                           p_west_east=i, p_east_west=j,
                                           p_north_south=k, p_south_north=l)

                        print('Starting Episode ' + str(e) + '...')

                        # this is the normal way of using traci. sumo is started as a
                        # subprocess and then the python script connects and runs
                        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                    "--time-to-teleport", "-1",
                                     "--tripinfo-output", "tripinfo.xml", '--start', '-Q'], label='contestant')
                        # Connection to simulation environment
                        conn = traci.getConnection("contestant")
                        # Run a complete simulation episode with the agent taking actions for as long as the episode lasts.
                        # An episode lasts as long as there are cars in the simulation AND the time passed < 1000 seconds
                        total_waiting_time, waiting_times, total_emissions = run_episode(
                            conn, agent, COMPETITION_ROUND)
                        # Cleaning up TraCi environments
                        traci.switch("contestant")
                        traci.close()
                        # Calculate the avg waiting time per vehicle
                        avg_waiting_time = total_waiting_time / vehicles
                        avg_emissions = total_emissions / (1000 * vehicles)
                        total_of_totals += avg_waiting_time
                        waiting_time_per_episode.append(avg_waiting_time)

                        print('west = ' + str(i) + ', east = ' + str(j) +
                              ', north =  ' + str(k) + ', south = ' + str(l), end=' ')
                        print(' episode[' + str(e) + '] Average waiting time = ' + str(avg_waiting_time)
                              + ' (s) -- Average Emissions (CO2) = ' + str(avg_emissions) + "(g)")

                    probability_average = total_of_totals/NUM_EPISODES
                    average_answer += probability_average
                    if(probability_average < best_answer):
                        best_answer = probability_average
                        best_probability = [i, j, k, l]

                    if(probability_average > worst_answer):
                        worst_answer = probability_average
                        worst_probability = [i, j, k, l]

                    times_list.append(probability_average)
                    sys.stdout.write("\033[1;34m")
                    print('***TEST #' + str(counter) + ' west = ' + str(i) + ', east = ' + str(j) +
                          ', north =  ' + str(k) + ', south = ' + str(l), 'average = ' + str(probability_average))
                    sys.stdout.write("\033[0;0m")

    sys.stdout.write("\033[1;31m")
    print('======== TESTING FINISHED')
    print('Average answer = ' + str(average_answer/counter))
    print('Best Answer = ' + str(best_answer) + ' when probability = ' , best_probability)
    print('Worst Answer = ' + str(worst_answer) + ' when probability = ' , worst_probability)
    sys.stdout.write("\033[0;0m")