import pandas as pd
import numpy as np
import gym
import gym.spaces
import naoenv
import random
import math
import ast


class Learning:

    def __init__(self, memory):
        self.memory = memory
        self.memory.RLenv = gym.make('NaoEnv-v0')
        self.memory.RLenv.setup(memory)
        self.memory.q_table = np.zeros((self.memory.RL_states, self.memory.RL_actions))


    def prepareRL(self):
        # -------------------------------
        # setup the reinforcement learning, ini state
        # -------------------------------
        self.memory.RL_state = 0
        self.memory.trailDone = False

    def getAction(self):
        # -------------------------------
        # get an action from the possible actions with the use of the learned reinforcement learning
        # -------------------------------

        # get the best available action with the highest associated Q value
        bestAvailableAction = -1
        bestQValue = 0
        for possibleAction in self.memory.possibleActions:
            qValue = self.memory.q_table[self.memory.RL_state, possibleAction-1]

            if bestAvailableAction == -1 or qValue > bestQValue:
                bestAvailableAction = possibleAction
                bestQValue = qValue

        a = bestAvailableAction

        # sometimes do a random action (eps) or if there are no q_values yet
        eps = self.memory.RL_eps[self.memory.RL_state]
        if np.random.random() < eps or np.sum(self.memory.q_table[self.memory.RL_state, :]) == 0:
            a = random.choice(self.memory.possibleActions)

        return a

    def updateQtable(self, a, correctBall=False):
        # -------------------------------
        # update reinforcement learning given the results
        # -------------------------------
        new_s, self.memory.RL_r, self.memory.trialDone, _ = self.memory.RLenv.step(self.memory.RL_state, a, correctBall)
        old_q = self.memory.q_table[self.memory.RL_state, a - 1]
        self.memory.q_table[self.memory.RL_state, a-1] = (1 - self.memory.RL_lr) * self.memory.q_table[self.memory.RL_state, a-1] + self.memory.RL_lr * (self.memory.RL_r + self.memory.RL_y * np.max(self.memory.q_table[new_s, :]))
        new_q = self.memory.q_table[self.memory.RL_state, a-1]

        # Update epsilon for this state (before the action is taken)
        if not (a == 6 or a == 5 or a == 4):
            f_value = (1.0 - math.exp(-abs(new_q - old_q)/self.memory.RL_sigma))/(1.0 + math.exp(-abs(old_q - new_q)/self.memory.RL_sigma))
            self.memory.RL_eps[self.memory.RL_state] = self.memory.RL_delta * f_value + (1.0 - self.memory.RL_delta) * self.memory.RL_eps[self.memory.RL_state]

        self.memory.RL_state = new_s



    def saveStatistics(self):
        # -------------------------------
        # append the qtable to a history of qtables, write it to a csv file. (longterm memory)
        # -------------------------------
        # read csv file and convert it to a np array, then append the new qtable and save it again to a csv
        df = pd.read_csv("statistics.csv", )
        q_string = ""
        for j, sublist in enumerate(self.memory.q_table):
            q_string += "["
            for i, q in enumerate(sublist):
                q_string += str(q)
                if i < len(sublist)-1:
                    q_string += ","

            q_string += "]"
            if j < len(self.memory.q_table)-1:
                q_string += ","

        df2 = pd.DataFrame([[q_string, str( list(self.memory.RL_eps))]], columns=["qtable", "epsilon"])
        df = df.append(df2)
        print ("Epsilons:", self.memory.RL_eps)
        df.to_csv("statistics.csv", index=False)


    def getStatistics(self):
        # -------------------------------
        # gets the last qtable from the long term memory
        # -------------------------------
        df = pd.read_csv("statistics.csv")
        qtablelist = df["qtable"].values
        epsionlist = list(df["epsilon"].values)

        qtable_string = qtablelist[-1]
        epsilon = epsionlist[-1]

        self.memory.q_table = np.array(list(ast.literal_eval(qtable_string)))
        self.memory.RL_eps = ast.literal_eval(epsilon)

        print ("Epsilons:", self.memory.RL_eps)
        print ("q_table:", self.memory.q_table)
