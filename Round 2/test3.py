import os
import sys
import random
 
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
 
 
 
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
 
NUM_EPISODES_RANDOM = 20  # Number of complete simulation runs
NUM_EPISODES_BIASED = 20  # Number of complete simulation runs
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
GUI = False
if __name__ == "__main__":
 
    print('Starting Sumo...')
    # The normal way to start sumo on the CLI
    # comment the line above and uncomment the following one to instantiate the simulation with the GUI
    if (GUI):
        sumoBinary = checkBinary('sumo-gui')
    else:
        sumoBinary = checkBinary('sumo')
 
    agent = Agent()  # Instantiate your agent object
    # A list to hold the average waiting time per vehicle returned from every episode
    waiting_time_per_episode = []
    total_of_totals = 0
    p1 = 0.5  # west_east
    p2 = 0.5  # east_west
    p3 = 0.5  # north_south
    p4 = 0.5  #south_north
    print(bcolors.FAIL + '#################Starting the Random testing#################### ' + bcolors.ENDC)
 
    for e in range(NUM_EPISODES_RANDOM):
        # Generate an episode with the specified probabilities for lanes in the intersection
        # Returns the number of vehicles that will be generated in the episode
        vehicles = gen_sim('', round=COMPETITION_ROUND,
                           p_west_east=p1, p_east_west=p2,
                           p_north_south=p3, p_south_north=p4)
 
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
 
        print(bcolors.OKBLUE + 'episode[' + str(e) + '] Average waiting time = ' + str(avg_waiting_time)
              + ' (s) -- Average Emissions (CO2) = ' + str(avg_emissions) + "(g)")
 
        # average so far in random input
        print( "prefix average = ", str(total_of_totals /( e + 1)) + bcolors.ENDC)
    average_input_random = total_of_totals / NUM_EPISODES_RANDOM
    print(bcolors.FAIL + 'total_freaking_average when input is random  =  ' + str(average_input_random) + bcolors.ENDC)
 
 
 
    print(bcolors.FAIL + '#################Starting the biased testing#################### ' + bcolors.ENDC)
 
 
    waiting_time_per_episode = []
    total_of_totals = 0
    p1 = random.uniform(0, 0.3)  # west_east
    p2 = random.uniform(0.5 , 1)  # east_west
    p3 = random.uniform(0.7 , 1.0)  # north_south
    p4 = random.uniform(0.7,1.0)  # south_north
 
 
    for e in range(NUM_EPISODES_BIASED):
        # Generate an episode with the specified probabilities for lanes in the intersection
        # Returns the number of vehicles that will be generated in the episode
 
        permutation = [p1, p2, p3, p4]
        random.shuffle(permutation)
        p1 = permutation[0]
        p2 = permutation[1]
        p3 = permutation[2]
        p4 = permutation[3]
 
 
        vehicles = gen_sim('', round=COMPETITION_ROUND,
                           p_west_east=p1, p_east_west=p2,
                           p_north_south=p3, p_south_north=p4)
 
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
 
 
        print(bcolors.OKBLUE + 'p1 = ' + str(p1) + ' p2 = ' + str(p2) + ' p3 = ' + str(p3 ) + ' p4 = ' , str(p4))
        print('episode[' + str(e) + '] Average waiting time = ' + str(avg_waiting_time)
              + ' (s) -- Average Emissions (CO2) = ' + str(avg_emissions) + "(g)" + bcolors.ENDC)
 
        # average so far in random input
        print(bcolors.OKBLUE + "prefix average = ", str(total_of_totals / (e + 1)) + bcolors.ENDC)
    average_input_biased = total_of_totals / NUM_EPISODES_BIASED
 
    print(bcolors.FAIL + 'total_freaking_average when input is random  =  ' + str(average_input_random) + bcolors.ENDC) # I print it again here
    print(bcolors.FAIL + 'total_freaking_average when input is biased  =  ' + str(average_input_biased) + bcolors.ENDC)
 
 
    print("Attention please !!! ")
    print(bcolors.FAIL + 'average of all ' + str(NUM_EPISODES_BIASED + NUM_EPISODES_RANDOM) + ' episodes are ' , str((average_input_biased + average_input_random)/2) + bcolors.ENDC)