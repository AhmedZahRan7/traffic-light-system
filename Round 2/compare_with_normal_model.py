import os
import sys
import numpy
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

from sumolib import checkBinary
import traci 
import random
from Agent import Agent
from normal_model import normalAgent
from sumo_utils_rnd2 import run_episode
from gen_sim_rnd2 import gen_sim
NUM_EPISODES = 5
COMPETITION_ROUND = 2
SampleList = []
normalTime = []
normalEmission = []
agentTime = []
agentEmission = []

if __name__ == "__main__":
    print('Starting Sumo...')
    sumoBinary = checkBinary('sumo')
    # sumoBinary = checkBinary('sumo-gui')
    f = open("file.txt", "w")
    f.write("THIS TEST RUNS ON {} SAMPLES".format(NUM_EPISODES))
    for distStart in numpy.arange(0,1,.1):
        for distEnd in numpy.arange(distStart+.1,1,.1):
            SampleList.append([distStart,distEnd])
            waiting_time_per_episode = []
            agent = Agent()
            agentTotalTime = 0
            agentTotalemission = 0
            f.write("## OUR MODEL ON UNIFORM DIST FROM {} TO {}\n".format(distStart,distEnd))
            print(bcolors.HEADER + "## OUR MODEL ON UNIFORM DIST FROM {} TO {}\n".format(distStart,distEnd) + bcolors.ENDC)
            for e in range(NUM_EPISODES):
                vehicles = gen_sim('', round=COMPETITION_ROUND,
                                p_west_east=random.uniform(distStart,distEnd), p_east_west=random.uniform(distStart,distEnd),
                                p_north_south=random.uniform(distStart,distEnd), p_south_north=random.uniform(distStart,distEnd))

                print('Starting Episode ' + str(e) + '...')
                traci.start([sumoBinary, "-c", "data/cross.sumocfg","--time-to-teleport", "-1","--tripinfo-output", "tripinfo.xml", '--start', '-Q'], label='contestant')
                conn = traci.getConnection("contestant")
                total_waiting_time, waiting_times, total_emissions = run_episode(conn, agent, COMPETITION_ROUND)
                traci.switch("contestant")
                traci.close()
                avg_waiting_time = total_waiting_time / vehicles
                avg_emissions = total_emissions / (1000 * vehicles)
                waiting_time_per_episode.append(avg_waiting_time)
                print('episode[' + str(e) + '] Average waiting time = ' + str(avg_waiting_time)+' (s) -- Average Emissions (CO2) = ' + str(avg_emissions) + "(g)")
                agentTotalTime += avg_waiting_time
                agentTotalemission += avg_emissions
            f.write("avg time is {} , avg emission is {}\n".format(agentTotalTime/NUM_EPISODES,agentTotalemission/NUM_EPISODES))
            print(bcolors.OKGREEN + "avg time is {} , avg emission is {}\n".format(agentTotalTime/NUM_EPISODES,agentTotalemission/NUM_EPISODES) + bcolors.ENDC)
            agentTime.append(agentTotalTime/NUM_EPISODES)
            agentEmission.append(agentTotalemission/NUM_EPISODES)

            normalModel = normalAgent()
            agentTotalTime = 0
            agentTotalemission = 0
            waiting_time_per_episode = []
            print(bcolors.HEADER + "## NORMAL MODEL ON UNIFORM DIST FROM {} TO {}\n".format(distStart,distEnd) + bcolors.ENDC)
            f.write("## NORMAL MODEL ON UNIFORM DIST FROM {} TO {}\n".format(distStart,distEnd))
            for e in range(NUM_EPISODES):
                vehicles = gen_sim('', round=COMPETITION_ROUND,
                                p_west_east=random.uniform(distStart,distEnd), p_east_west=random.uniform(distStart,distEnd),
                                p_north_south=random.uniform(distStart,distEnd), p_south_north=random.uniform(distStart,distEnd))

                print('Starting Episode ' + str(e) + '...')
                traci.start([sumoBinary, "-c", "data/cross.sumocfg","--time-to-teleport", "-1","--tripinfo-output", "tripinfo.xml", '--start', '-Q'], label='contestant')
                conn = traci.getConnection("contestant")
                total_waiting_time, waiting_times, total_emissions = run_episode(conn, normalModel, COMPETITION_ROUND)
                traci.switch("contestant")
                traci.close()
                avg_waiting_time = total_waiting_time / vehicles
                avg_emissions = total_emissions / (1000 * vehicles)
                waiting_time_per_episode.append(avg_waiting_time)
                print('episode[' + str(e) + '] Average waiting time = ' + str(avg_waiting_time)+' (s) -- Average Emissions (CO2) = ' + str(avg_emissions) + "(g)")
                agentTotalTime += avg_waiting_time
                agentTotalemission += avg_emissions
            f.write("avg time is {} ,emission is {}\n".format(agentTotalTime/NUM_EPISODES,agentTotalemission/NUM_EPISODES))
            print(bcolors.FAIL + "avg time is {} , avg emission is {}\n".format(agentTotalTime/NUM_EPISODES,agentTotalemission/NUM_EPISODES) + bcolors.ENDC)
            normalTime.append(agentTotalTime/NUM_EPISODES)
            normalEmission.append(agentTotalemission/NUM_EPISODES)
    
    print("Samples")
    print(SampleList)
    print("Normal avg time")
    print(normalTime)
    print("Normal avg emission")
    print(normalEmission)
    print("Agent avg time")
    print(agentTime)
    print("Agent avg emission")
    print(agentEmission)
    
    f.write("Samples")
    f.write(SampleList)
    f.write("Normal avg time")
    f.write(normalTime)
    f.write("Normal avg emission")
    f.write(normalEmission)
    f.write("Agent avg time")
    f.write(agentTime)
    f.write("Agent avg emission")
    f.write(agentEmission)
    