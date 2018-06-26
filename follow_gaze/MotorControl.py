import naoqi
import pandas as pd
import numpy as np
import Perception
from time import sleep
import math

class MotorControl:

    def __init__(self, motionProxy, memory, facePerception, tts):
        self.Action = False
        self.tts = tts
        self.motionProxy = motionProxy
        self.memory = memory
        self.cam = memory.camera
        self.facePerception = facePerception

    def followVec(self, Vec, distance = 250):
        # -------------------------------
        # follows a given vector for a given distance
        # -------------------------------

        goal = [0,0]
        vector = [Vec[0]-Vec[2], Vec[1]-Vec[3]]

        # get the direction in which to follow the vector
        direction = 1
        if vector[0] >= 0:
            direction = -1

        vertical_direction = -1
        if vector[1] <= 0:
            vertical_direction = 1

        if vector[1]== 0:
            move_in_x = distance*direction
            move_in_y = 0
        elif vector[0] == 0:
            move_in_x = 0
            move_in_y = distance*vertical_direction
        else:
            gradient = float(vector[1])/float(vector[0])
            distPerx = np.sqrt(1 + (gradient ** 2))
            move_in_x = (float(distance) / distPerx) * direction
            move_in_y = gradient * move_in_x

        # set the goal coords
        goal[0] = (move_in_x) * self.cam.HRatioDtoP
        goal[1] = (move_in_y) * self.cam.VRatioDtoP

        #setup the movement of the head and perform it
        joints = ["HeadYaw", "HeadPitch"]
        times = [[0.6], [0.6]]  # time in seconds
        angles = [-goal[0] * math.pi / 180, goal[1] * math.pi / 180]  # change to -1, 1 so we move up left is - -  down right is + +
        self.motionProxy.angleInterpolation(joints, angles, times, False)

        return True


    def centerGazeStart(self, gaze):
        # -------------------------------
        # given the gaze center the starting point
        # -------------------------------
        goal = [0, 0]
        goal[0] = (self.cam.center[0] + (self.cam.center[0] - gaze[0])) * self.cam.HRatioDtoP
        goal[0] = (self.cam.center[1] + (self.cam.center[1] - gaze[1])) * self.cam.VRatioDtoP
        moved = self.moveTo(goal)
        return moved

    def pointAtObject(self, ObjectCords,  isAbsolut = True):
        # -------------------------------
        # pointing with the arm at a given object
        # -------------------------------

        #centers with the head the object to point at
        self.centerObject(ObjectCords)

        #check the dead angles and check which arm to use, left or right
        head = ["HeadYaw", "HeadPitch"]
        headAngels = self.motionProxy.getAngles(head, True)
        if headAngels[0] <= 0:
            side = "Right"
        elif headAngels[0]> 0:
            side = "Left"

        # given the left or right arm set the joint values the robot should set the arm to
        joints = []
        if side == "Left":
            joints = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]
            direction = 1
            shoulderRollOffset = -0.2
            shoulderPitchOffset = -0.2
            startpoint = self.motionProxy.getAngles(joints, True)

        elif side == "Right":
            joints = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
            direction = -1
            shoulderRollOffset = 0.2
            shoulderPitchOffset = -0.2
            startpoint = self.motionProxy.getAngles(joints, True)

        #setup speed and angles and perform the motion, sleep 2 seconds before returning to start position
        times = [[0.8], [0.8], [0.8], [0.8], [0.8], [0.8]]
        angels = [[headAngels[1]+shoulderPitchOffset], [headAngels[0]+shoulderRollOffset], [0], [1.3*direction], [0], [0]]
        self.motionProxy.angleInterpolation(joints, angels, times, isAbsolut)
        sleep(2)
        self.motionProxy.angleInterpolation(joints, startpoint, times, isAbsolut)

        return True


    def look(self, horizontal, vertical, stepsizeH = 0.5, stepsizeV =0.15, isAbsolute = False):
        # -------------------------------
        # looking left right up or down.
        # -------------------------------

        #setup the head joints, speed and angles
        joints = ["HeadYaw", "HeadPitch"]
        times = [[0.6], [0.6]]  # time in seconds
        angles = [[0], [0]]

        #put the destination angles for the given input of horizontal and vertical
        if vertical == "center":
            angles[1] = 0
        elif vertical == "up":
            angles[1] = stepsizeV
        elif vertical == "down":
            angles[1] = -stepsizeV
        else:
            print("invalid input for MC::look")
            return False

        if horizontal == "center":
            angles[0] = 0
        elif horizontal == "left":
            angles[0] = stepsizeH
        elif horizontal == "right":
            angles[0] = -stepsizeH
        else:
            print("invalid input for MC::look")
            return False

        #look in the given direction
        print "Looking ", horizontal," ",vertical
        self.motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

        return True


    def moveTo(self, goal, isAbsolute = False):
        # -------------------------------
        # given a goal coord in the camera image move the head to center that point
        # -------------------------------
        #ini head joints and speed
        joints = ["HeadYaw", "HeadPitch"]
        times = [[0.6], [0.6]]  # time in seconds

        #translate from degree to rad and perform the motion
        angles = [-goal[0]*math.pi/180, goal[1]*math.pi/180]
        self.motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

        return True

    def centerObject(self, object):
        # -------------------------------
        # given a object center it.
        # -------------------------------
        #calculate the joint distance in degrees form the camera center to the object
        goal = [0, 0]
        goal[0] = (object[0] - self.cam.center[0]) * self.cam.HRatioDtoP
        goal[1] = (object[1] - self.cam.center[1]) * self.cam.VRatioDtoP
        self.moveTo(goal)

    def findAndCenterFace(self, faceFound = False):
        # -------------------------------
        # looks for a face and if one is found center it
        # -------------------------------

        #a given predifined path to look for the face
        findFacePath = [["left", "center"],["right", "center"],["right", "center"], ["left", "center"]]

        # if no face found move head and look for face
        if faceFound == False:
            for i in range(0, len(findFacePath) + 1):
                self.facePerception.getFace()
                face = self.memory.face
                if face != []:
                    faceFound = True
                    break
                elif i < len(findFacePath):
                    self.look(findFacePath[i][0], findFacePath[i][1])
        # if no face could be found report it else center face
        if faceFound == False :
            self.tts.say("No face found")
            return False
        else:
            faceInCenter = False
            runs = 0
            #until the face is not fentered try 5 times to center it.
            while faceInCenter is False and runs < 5:
                runs = runs + 1
                #get a face
                self.facePerception.getFace()
                face = self.memory.face
                faceCentered = self.memory.faceCentered
                print "Face in center on face:", face
                #if face is in center report it, else center the face coords
                if faceCentered:
                    faceInCenter = faceCentered
                    self.tts.say("Face centered")
                elif face != []:
                    goal = [0,0]
                    goal[0] = (face[0] - self.cam.center[0]) * self.cam.HRatioDtoP
                    goal[1] = (face[1] - self.cam.center[1]) * self.cam.VRatioDtoP
                    self.moveTo(goal)

        #when no face could be centered after 5 tries report it
        if faceInCenter==False:
            self.tts.say("Face can not be centered")

        return faceInCenter
