import numpy as np
import pandas as pd
import Motivation as Moti
import Memory as memo
import MotorControl as MC
import Perception
import time



class Decision:

    def __init__(self, memory, learning):
        self.learning = learning
        self.memory = memory
        self.decision = False
        self.objectThreshold = False


    def makeDecision(self):
        # -------------------------------
        # makes a decision given the state
        # -------------------------------

        #get some bools important for the decision making
        motivation = self.memory.motivation
        Face = self.memory.face
        GazeEyeContact = self.memory.havingEyeContact
        FaceCentered = self.memory.faceCentered
        HadEyeContact = self.memory.hadEyeContact
        sentence = False
        decision = False

        if motivation == "SearchForObject":
            correctBall = False

            # choose an action to do
            a = self.learning.getAction()

            # if a == 1 or a == 2 or a == 3:
            #     a = 3

            if a == 1:
                decision = "LookLeft"
            elif a == 2:
                decision = "LookRight"
            elif a == 3:
                decision = "FollowGaze"
            elif a == 4:
                decision = "ChoseCloseBall"
                i = self.memory.distToBalls.index(min(self.memory.distToBalls))
                self.memory.ballChosen = i
                correctBall = self.checkIfCorrectBall()
            elif a == 5:
                decision = "ChoseFarBall"
                i = self.memory.distToBalls.index(max(self.memory.distToBalls))
                self.memory.ballChosen = i
                correctBall = self.checkIfCorrectBall()
            elif a == 6:
                decision = "Wait"

            self.learning.updateQtable(a, correctBall)

        elif motivation == "SearchForFace":
            decision = "SearchForFace"
        elif motivation == "CenterFace":
            decision = "CenterFace"
        elif motivation == "WaitForEyeContact":
            decision = "WaitForEyeContact"

            if self.memory.patience == 0:
                self.memory.patience = time.time()
            elif (time.time() - self.memory.patience) > self.memory.maxPatience:
                self.memory.patience = 0
                self.memory.hadEyeContact = True
                sentence = "I ran out of patience"
                time.sleep(2)
                print ("slep for 2 seconds")

        elif FaceCentered and GazeEyeContact == True and HadEyeContact == True:
            decision = "WaitForLosingEyeContact"
        elif motivation == "Wait":
            decision = "Wait"

        self.memory.decision = decision

        return sentence

    def checkIfCorrectBall(self):
        # -------------------------------
        # checking the the ball which has been selected is actually the right ball the person look at
        # -------------------------------
        correctBall = self.memory.lastBallColors[self.memory.ballChosen] is self.memory.correctObject
        print "Picked ball, correct ball?:", correctBall
        return correctBall

    def getPossibleActions(self, state, distances, headAngles):
        # -------------------------------
        # given the state, distance from the ball to the followed vector , and the angles of the head, list all possible
        # action the robot can perform as next action
        # -------------------------------

        print "State in get possible actions:", state
        #ini possible actions to empty list
        self.memory.possibleActions = []
        #if the state is 0 then only action 1,2,3 are available, return here
        if state == 0:
            self.memory.possibleActions = [1,2,3]
            return True

        # if the head moved out of the range then the robot can not continue to follow the given vector
        if headAngles[0] > -1.43 and headAngles[0] < 1.37 and headAngles[1] > -0.31 and headAngles[1] < 0.4:
            self.memory.possibleActions.append(state)
        else:
            print "out of bounds"

        if state not in [1, 2, 3]:
            print("error in get action: action state not 1,2, or 3")
            return True

        #check if the given balls are far away of close by the followed vector.

        #threshold is the middle point between resolution x and y (640 and 420 t = 530*0.1 = 53) 10% of the middle
        threshold = ((self.memory.camera.resolutionY+self.memory.camera.resolutionX)/2) * (self.memory.camera.boundpercent / 100.0) + self.memory.gazeFollowCounter * self.memory.gazeFollowThresholdIncr
        print ("Threshold for ball closeby:", threshold, " with counter:", self.memory.gazeFollowCounter)

        faraway = False
        closeby = False
        for dist in distances:
            if dist < threshold:
                closeby = True
            else:
                faraway = True

        if closeby:
            self.memory.possibleActions.append(4)
        if faraway:
            self.memory.possibleActions.append(5)

        if self.memory.possibleActions == []:
            self.memory.possibleActions.append(6)

        return True
