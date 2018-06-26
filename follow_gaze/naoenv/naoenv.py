import gym
from gym import spaces
from gym.utils import seeding

class NaoEnv(gym.Env):
    """n-Chain environment
    This game presents moves along a linear chain of states, with two actions:
     0) forward, which moves along the chain but returns no reward
     1) backward, which returns to the beginning and has a small reward
    The end of the chain, however, presents a large reward, and by moving
    'forward' at the end of the chain this large reward can be repeated.
    At each action, there is a small probability that the agent 'slips' and the
    opposite transition is instead taken.
    The observed state is the current state in the chain (0 to n-1).
    This environment is described in section 6.1 of:
    A Bayesian Framework for Reinforcement Learning by Malcolm Strens (2000)
    http://ceit.aut.ac.ir/~shiry/lecture/machine-learning/papers/BRL-2000.pdf
    """
    def __init__(self, slip=0.2):
        self.slip = slip  # probability of 'slipping' an action
        self.small = 0  # payout for 'backwards' action
        self.large = 10  # payout at end of chain for 'forwards' action

    def setup(self, memory):
        self.memory = memory
        self.state = self.memory.RL_state  # Start at beginning of the chain
        self.action_space = spaces.Discrete(self.memory.RL_actions)
        self.observation_space = spaces.Discrete(self.memory.RL_states)
        self.seed()

        # state, ID
        # ----------
        # start, 0
        # looked_left, 1
        # looked_right, 2
        # followed_gaze, 3
        # chose_ball_close_by, 4
        # chose_ball_far_away, 5
        # terminated, 6

        # action, ID
        # ----------
        # look_left, 1
        # look_right, 2
        # follow_gaze, 3
        # choose_ball_close_by, 4
        # choose_ball_far_away, 5
        # terminate, 6

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, state, action, correctBall=False):
        assert self.action_space.contains(action-1)

        done = False
        print "State", self.state, "-> do action:", action

        reward = 0

        # if self.np_random.rand() < self.slip:
        #     action = not action  # agent slipped, reverse action taken

        # each action leads to an end state (for now)
        if action == 1:
            self.state = 1

        elif action == 2:
            self.state  = 2

        elif action == 3:
            self.state = 3

        elif action == 4:
            self.state = 4

            reward = self.memory.defaultReward
            if correctBall:
                reward = self.memory.rewardCorrectBall

            done = True

        elif action == 5:
            self.state = 5

            reward = self.memory.defaultReward
            if correctBall:
                reward = self.memory.rewardCorrectBall

            done = True

        elif action == 6:
            reward = self.memory.defaultReward
            self.state = 6
            done = True

        return self.state, reward, done, {}
