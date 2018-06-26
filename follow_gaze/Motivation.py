import pandas as pd
import numpy as np
import Perception as perc


class Motivation:

    def __init__(self, memory):
        self.memory = memory

    def getMotivation(self):
        # -------------------------------
        # get the motivation of the robot given some bools
        # -------------------------------

        #get some bools and the face
        Face = self.memory.face
        GazeEyeContact = self.memory.havingEyeContact
        FaceCentered = self.memory.faceCentered
        HadEyeContact = self.memory.hadEyeContact

        print "Deciding moti: Face ", Face, " EyeContact", GazeEyeContact, " FaceCent:", FaceCentered, " HadEyeContact ", HadEyeContact

        #ini moti is just to wait
        moti = "Wait"

        # if we have been looking for the object for some time, don't require the face anymore
        if (Face != [] or self.memory.motivation == "SearchForObject") and GazeEyeContact == False and HadEyeContact == True:
            moti = "SearchForObject"
        elif FaceCentered == False and Face !=[]:
            moti = "CenterFace"
        elif Face == []:
            moti = "SearchForFace"
        elif FaceCentered and GazeEyeContact == False and HadEyeContact == False:
            moti = "WaitForEyeContact"

        self.memory.motivation = moti
        return True
