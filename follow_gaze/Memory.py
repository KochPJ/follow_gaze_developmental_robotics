import Perception as perc
import pandas as pd
import numpy as np


class Memory:

    def __init__(self, camera):
        self.camera = camera
        self.decision = False
        # self.evaluation = False
        # self.DecisionProbabilities = False
        # self.ObjectProbabilities = False

        # Ball perception
        self.lastBallCenters = False
        self.lastBallColors = False
        self.lastballsCount = False
        self.lassBallRadius = False
        self.distToBalls = []
        self.ballChosen = False # index to chosen ball in list of current balls found

        # Face perception
        self.face = []
        self.faceUpperLeft = False # coordiante of upper left corner of face rectangle
        self.eye = False
        self.faceCentered = False
        self.hadEyeContact = False
        self.havingEyeContact = False


        # learning
        self.correctObject = "green"
        self.RLenv = False
        self.q_table = False

        self.RL_y = 0.8 # discount factor
        self.RL_eps = np.ones(4)
        self.RL_delta = 0.05
        self.RL_sigma = 20.0
        self.RL_lr = 0.2
        self.RL_state = 0
        self.trialDone = False

        self.defaultReward = -0.2
        self.rewardCorrectBall = 5

        self.RL_states = 7 # start, looking left/right, following_gaze, picked close/far, terminate
        self.RL_actions = 6 # look left, look right, follow gaze, pick close/far, terminate


        # Gaze
        self.gazeVector = False
        self.gazeFollowCounter = 0
        self.gazeFollowThresholdIncr = 30

        # Memory
        self.motivation = False

        # OS
        self.OS = "Windows"

        # DecisionMaking
        self.actions = False
        self.patience = 0
        self.maxPatience = 10.0


    def resetVars(self):
        # -------------------------------
        # reset the memory to ini values
        # -------------------------------
        self.lastBallCenters = False
        self.lastBallColors = False
        self.lastballsCount = False
        self.lassBallRadius = False
        self.distToBalls = []
        self.ballChosen = False

        self.RL_state = 0
        self.trialDone = False

        self.gazeFollowCounter = 0
        self.gazeVector = False

        self.face = []
        self.faceUpperLeft = False
        self.eye = False
        self.faceCentered = False
        self.hadEyeContact = False
        self.havingEyeContact = False
        self.patience = 0
