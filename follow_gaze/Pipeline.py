import cv2, sys
import numpy as np
import pandas as pd
from time import sleep
import traceback
from naoqi import ALModule, ALProxy, ALBroker

import Perception as Perc
import Memory as memo
import Learning as Learn
import Decision as Deci
import Motivation as Moti
import MotorControl as MC


# Import architecture modules
# import camera


# general variables
ip = "192.168.1.104"
port = 9559
duration = 600


#initiate proxies
try:
    postureProxy = ALProxy("ALRobotPosture", ip ,port )
    tts = ALProxy("ALTextToSpeech", ip , port )
    mem = ALProxy("ALMemory", ip, port)
    motionProxy = ALProxy("ALMotion", ip ,port )
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
except Exception, e:
    print "could not create all proxies"
    print "error was ", e
    sys.exit(1)

# disable ALAutonomousMoves bug
am = ALProxy("ALAutonomousMoves", ip ,port )
am.setExpressiveListeningEnabled(False)
am.setBackgroundStrategy("none")



#######Global classes#######
camera = Perc.Camera()
memory = memo.Memory(camera)
facePerception = Perc.Face(memory)
gazeFollowing = Perc.Gaze(memory)
ballPerception = Perc.Ball(memory)
learning = Learn.Learning(memory)
decision = Deci.Decision(memory, learning)
motivation = Moti.Motivation(memory)
motorControl = MC.MotorControl(motionProxy, memory, facePerception, tts)


################################################################
# Main functions
################################################################

def setup():
    say("Setting up")
    postureProxy.goToPosture("Crouch", 0.6667)


def say(text):
    tts.say(text)
    print text



def pipeline():

    try:
        setup()
        camera.cameraSetup(ip, port)
        say("Starting")
        learning.getStatistics()

        # main loop
        ballColours = colors = ["green", "pink"]
        cont = True
        trial = 0
        while cont:
            trial += 1
            # prepare for new trial
            learning.prepareRL()
            memory.resetVars()
            postureProxy.goToPosture("Crouch", 0.6667)

            say("\nStarting trial " + str(trial))

            # learning.saveStatistics()
            # print("Written statistics to file")

            # Do all actions untill an exit node was found (found ball or max head movement)
            while not memory.trialDone:

                # do face and ball detection
                facePerception.getFace()
                ballPerception.getBall(ballColours)
                print "\nFace:", memory.face, "Eye:", memory.eye, "faceCentered", memory.faceCentered
                print "Balls found:", memory.lastballsCount, " Ball centers:", memory.lastBallCenters
                ballPerception.drawCircle(memory.lastBallCenters, memory.lassBallRadius)

                # get the motivation
                motivation.getMotivation()
                # memory.motivation = "SearchForObject"
                moti = memory.motivation
                print "motivation = ", moti

                # determine the distances of the found balls to the (gaze) vector we are following
                # only check if we are actually following a vector (not state 0)
                if memory.RL_state != 0 and memory.lastballsCount > 0:
                    if deci == "LookLeft" or deci == "LookRight":
                        ballPerception.distToVec([0, memory.camera.resolutionY / 2, memory.camera.resolutionX, memory.camera.resolutionY / 2], memory.lastBallCenters)
                    elif deci == "FollowGaze":
                        ballPerception.distToVec(memory.gazeVector, memory.lastBallCenters)
                    print "Dist to balls:", memory.distToBalls

                # get possible actions and make a decision
                head = ["HeadYaw", "HeadPitch"]
                headAngels = motionProxy.getAngles(head, True)
                decision.getPossibleActions(memory.RL_state, distances=memory.distToBalls, headAngles=headAngels)
                print "Possible actions:", memory.possibleActions

                sentence = decision.makeDecision()
                if sentence:
                    say(sentence)
                deci = memory.decision
                print"decision = ", deci


                if deci == "Wait":
                    print("Waiting")
                    sleep(0.2)

                elif deci == "SearchForFace":
                    say(" Searching For Face")
                    faceCentered = motorControl.findAndCenterFace()
                    print("Face centered = ", faceCentered)

                elif deci == "CenterFace":
                    say("Centering Face")
                    faceCentered = motorControl.findAndCenterFace(faceFound=True)
                    print("Face centered = ", faceCentered)

                elif deci == "WaitForEyeContact":
                    # real gaze following (if you have caffe installed)
                    print "Get gaze"
                    gazeFollowing.getGaze()

                    print "Gaze vector:", memory.gazeVector
                    print "Face Centered:", memory.faceCentered

                    if memory.gazeVector:
                        facePerception.checkEyeContact()

                        if memory.havingEyeContact:
                            memory.hadEyeContact = True
                            say("We have eye contact!")

                        print ("Having eye contact:", memory.havingEyeContact, " Had eye contact:",  memory.hadEyeContact)


                elif deci == "WaitForLosingEyeContact":
                    print "Get gaze"
                    gazeFollowing.getGaze()

                    print "Gaze vector:", memory.gazeVector
                    print "Face Centered:", memory.faceCentered

                    if memory.gazeVector:
                        facePerception.checkEyeContact()

                        if not memory.havingEyeContact:
                            say("You looked away!")
                            sleep(2)
                            print ("slep for 2s")
                            print "Get gaze"
                            gazeFollowing.getGaze()
                        else:
                            print "Still having eyecontact"


                elif deci == "LookLeft":

                    say("I'm going to look left")
                    # start looking left
                    memory.gazeVector = [0, 0, -memory.camera.resolutionX / 2, 0]
                    motorControl.followVec(memory.gazeVector)


                elif deci == "LookRight":
                    say("I'm going to look right")
                    # start looking right
                    memory.gazeVector = [0, 0, memory.camera.resolutionX / 2, 0]
                    motorControl.followVec(memory.gazeVector)


                elif deci == "FollowGaze":
                    if memory.gazeVector:
                        say("I'm going to follow your gaze")
                        # only center on the gaze the first time
                        if memory.gazeFollowCounter == 0:
                            print "Centering on gaze"
                            motorControl.centerObject([memory.gazeVector[0], memory.gazeVector[1]])


                        print "Following gaze"
                        motorControl.followVec(memory.gazeVector)
                        memory.gazeFollowCounter += 1
                    else:
                        say("I lost the gaze, so I can't follow the gaze")
                        gazeFollowing.getGaze()

                elif deci == "ChoseCloseBall":
                    say("I choose a close ball, pointing now")
                    motorControl.pointAtObject(memory.lastBallCenters[memory.ballChosen])
                    postureProxy.goToPosture("Crouch", 0.6667)

                elif deci == "ChoseFarBall":
                    say("I choose a far ball, pointing now")
                    motorControl.pointAtObject(memory.lastBallCenters[memory.ballChosen])
                    postureProxy.goToPosture("Crouch", 0.6667)


                if cv2.waitKey(33) == 27:
                    camera.videoProxy.unsubscribe(camera.cam)
                    break


            say("Trial " + str(trial) + " done\n\n")
            learning.saveStatistics()
            print("Written statistics to file")

            raw_input("Continue?")
            print ("Continuing!")

        say("Bye!")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        traceback.print_exc()
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        say("I am now shutting down.")
        print ("Shutting down")
        sleep(1.0)
        # rest
        postureProxy.goToPosture("Crouch", 0.6667)
        motionProxy.rest()
        pythonBroker.shutdown()
        gazeFollowing.quitMatlab()
        sys.exit(0)


if __name__ == "__main__":
    pipeline()
