import numpy as np

from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

import Env_wrapper

import traci

env = Env_wrapper.SumoWrapper()
states = 9
actions = 2

#episodes = 10 
#for episode in range(1, episodes + 1): 
#    state = env.reset()
#    done = False
#    score = 0

#    while not done:
#        env.render()
#        action = random.choice([0, 1])
#        n_state, reward, done, info = env.step(action)
#        score += reward
#    print('Episode {} score : {}'.format(episode, score))


def build_model(states, actions): 
    model = Sequential()
    model.add(Flatten(input_shape=(1, states)))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model



def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                nb_actions=actions, nb_steps_warmup=100, target_model_update=1e-3)
    return dqn


if __name__ == "__main__" :
    model = build_model(states, actions)

    dqn = build_agent(model, actions)
    dqn.compile(Adam(lr=1e-6), metrics=['mae'])
    dqn.load_weights('dqn_weights.h5f')
    dqn.fit(env, nb_steps=50000, visualize=False, verbose=3)
    traci.switch("contestant")
    traci.close()


    scores = dqn.test(env, nb_episodes=10, visualize=False)
    print(np.mean(scores.history['episode_reward']))

    dqn.save_weights('dqn_weights.h5f', overwrite=True)
