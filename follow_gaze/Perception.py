import cv2
import numpy as np
import naoqi
from time import sleep
import numpy.linalg

import matlab.engine


face_cascade = cv2.CascadeClassifier('./opencv_files/haarcascade_frontalface_default.xml')
left_eye_cascade = cv2.CascadeClassifier('./opencv_files/haarcascade_lefteye_2splits.xml')
right_eye_cascade = cv2.CascadeClassifier('./opencv_files/haarcascade_righteye_2splits.xml')
profile_face_cascade = cv2.CascadeClassifier('./opencv_files/haarcascade_profileface.xml')
eye_cascade = cv2.CascadeClassifier('./opencv_files/haarcascade_eye.xml')

class Camera:

    def __init__(self):
        self.img = False
        self.videoProxy = False
        self.cam = False
        self.resolution = 2  # 1 = 320to240, 2= 640to480, 3=1280to720
        self.resolutionX = 640
        self.resolutionY = 480
        self.HFOV = 60.9 # in degree
        self.VFOV = 47.6 # indegree

        self.center = [(self.resolutionX / 2), (self.resolutionY / 2)]
        self.boundpercent = 10
        self.boundx = self.center[0] / self.boundpercent
        self.boundy = self.center[1] / self.boundpercent#
        self.rangeX = [(self.center[0] - self.boundx), (self.center[0] + self.boundx)]
        self.rangeY = [(self.center[1] - self.boundy), (self.center[1] + self.boundy)]
        self.HRatioDtoP = self.HFOV / self.resolutionX
        self.VRatioDtoP = self.VFOV / self.resolutionY

    def cameraSetup(self, ip, port):
        # -------------------------------
        # sets up the camera
        # -------------------------------

        #set up proxy
        self.videoProxy = naoqi.ALProxy('ALVideoDevice', ip, port)

        cam_name = "camera"
        cam_type = 0
        res = self.resolution
        colspace = 13
        fps = 30

        cams = self.videoProxy.getSubscribers()
        for cam in cams:
            self.videoProxy.unsubscribe(cam)

        self.cam = self.videoProxy.subscribeCamera(cam_name, cam_type, res, colspace, fps)

        print "Succesfully connected camera"


        return

    def getImg(self, saveImg=False):
        # -------------------------------
        # gets an image form the robot camera. Saves the image to some png if wanted, needed for gaze detection
        # -------------------------------

        img = False
        try:
            image_container = self.videoProxy.getImageRemote(self.cam)
            width = image_container[0]
            height = image_container[1]
            values = map(ord, list(image_container[6]))
            img = np.array(values, np.uint8).reshape((height, width, 3))
            # cv2.imshow("Camera", img)
        except:
            print "missed frame (or error)"
            # print "Unexpected error:", sys.exc_info()[0]
            pass

        if saveImg:
            cv2.imwrite("currentView.png", img)


        return img

    def findFace(self, img):  # default ballcolour to recognize is blue
        # -------------------------------
        # actually looks in the image and looks for faces
        # -------------------------------

        # detect faces
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        faceColor = (255, 0, 0)

        left_eye = []
        right_eye = []

        # search complete img for profile if no faces were detected
        if faces == ():
            faces = profile_face_cascade.detectMultiScale(gray, 1.3, 5)
            faceColor = (0,0,0)

        if faces != ():
            #get the face closest to the image center
            at_i = 0
            closest_dist = 0
            for i in range(len(faces)):
                (x, y, w, h) = faces[i]
                faceCoords = [x + 0.5 * w, y + 0.5 * h]

                dist = np.sqrt(((self.center[0] -faceCoords[0]) ** 2) + (
                            (self.center[1] - faceCoords[1]) ** 2))
                if i == 0:
                    at_i = i
                    closest_dist = dist
                elif dist < closest_dist:
                    closest_dist = dist
                    at_i = i

            (x,y, w, h) = faces[at_i]
            # draw rectangle around face
            cv2.rectangle(img, (x, y), (x + w, y + h), faceColor, 2)

            # search region of interest (face) for eyes
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            left_eye = left_eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in left_eye:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (51, 153, 255), 2)

            right_eye = right_eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in right_eye:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (51, 255, 255), 2)

            if left_eye is ():
                left_eye = []
            if right_eye is ():
                right_eye = []
        else:
            faces = []

        # To show face rectangles
        cv2.imshow("Camera", img)
        return (faces, left_eye, right_eye)

    # get center of detected face or eye, and return the coordinates
    def getCenter(self, foundObjects, ID):
        # -------------------------------
        # return the center of a given eye of face
        # -------------------------------
        [x, y, w, h] = foundObjects[ID]
        [midX, midY] = x + 0.5 * w, y + 0.5 * h
        return [midX, midY]

class Ball:
    def __init__(self, memory):
        self.memory = memory
        self.center = False
        self.radius = False
        self.color = False
        self.count = False
        self.color = False

    def drawCircle(self, centers, radius):
        # -------------------------------
        # drawing some circles a round the found balls to get some visual feedback which balls the robot found
        # -------------------------------

        img = self.memory.camera.getImg()

        length = sum(np.shape(centers))
        if length > 2:
            for i in range(len(centers)):
                cv2.circle(img, (centers[i][0], centers[i][1]), radius[i], (0, 255, 0), 2)
        elif length == 2:
            cv2.circle(img, (centers[0], centers[1]), radius, (0, 255, 0), 2)
        else:
            print("center is empty")

        cv2.imshow("Camera", img)

        if cv2.waitKey(33) == 27:
            self.memory.camera.videoProxy.unsubscribe(self.memory.camera.cam)

    def distToVec(self, Vec, ballCenters):
        # -------------------------------
        # get the distance from a given list of ball points and gets the distance to the given vector
        # -------------------------------

        VecStart = np.array([Vec[0],Vec[1]])
        VecEnd = np.array([Vec[2], Vec[3]])
        length = sum(np.array(ballCenters).shape)
        if length > 2:
            dist = []
            for ballCent in ballCenters:
                print(VecStart, VecEnd ,np.array(ballCent) )
                d = np.linalg.norm(np.cross(VecEnd-VecStart, VecStart - np.array(ballCent)))/ np.linalg.norm(VecEnd-VecStart)
                dist.append(d)
        elif length == 2:
            dist = np.linalg.norm(np.cross(VecEnd-VecStart, VecStart - np.array(ballCenters)))/ np.linalg.norm(VecEnd-VecStart)
        else:
            print("no balls given")

        self.memory.distToBalls = dist
        return True


    def getBall(self, ballColour):
        # -------------------------------
        # finds the balls in the image of the passed colors
        # -------------------------------

        #ini everything to a empty list
        self.memory.lastBallCenters = []
        self.memory.lastBallColors = []
        self.memory.lassBallRadius = []
        self.memory.lastballsCount = 0
        self.memory.distToBalls = []

        # get a new image from the camera
        image = self.memory.camera.getImg()

        if image is False:
            print "Got no image in getBall"
            return False

        #loop through the colors
        for color in ballColour:
            # set the color ranges in hsv for the given color
            if color == "pink":
                currentColor = "pink"
                lower_colour = np.array([130, 100, 100], dtype=np.uint8)
                upper_colour = np.array([180, 255, 255], dtype=np.uint8)
            elif color == "green":
                currentColor = "green"
                lower_colour = np.array([29, 86, 6], dtype=np.uint8)
                upper_colour = np.array([64, 255, 255], dtype=np.uint8)
            elif color == "yellow":
                currentColor = "yellow"
                lower_colour = np.array([20, 100, 100], dtype=np.uint8)
                upper_colour = np.array([60, 255, 255], dtype=np.uint8)
            elif color == "red":
                currentColor = "red"
                lower_colour = np.array([0, 100, 100], dtype=np.uint8)
                upper_colour = np.array([10, 255, 255], dtype=np.uint8)
                # red has an extra colur mask
                lower_colour2 = np.array([160, 100, 100], dtype=np.uint8)
                upper_colour2 = np.array([179, 255, 255], dtype=np.uint8)
            elif color == "blue":
                currentColor = "blue"
                lower_colour = np.array([70, 50, 50], dtype=np.uint8)
                upper_colour = np.array([170, 255, 255], dtype=np.uint8)

            # convert image to hsv
            hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            #make binary image from it
            color_mask = cv2.inRange(hsvImage, lower_colour, upper_colour)

            # red is on both sides of the hsv scale so we need to add both sides to each other
            if ballColour == "red":
                color_mask2 = cv2.inRange(hsvImage, lower_colour2, upper_colour2)
                color_mask = cv2.addWeighted(color_mask, 1.0, color_mask2, 1.0, 0)
                color_mask = cv2.GaussianBlur(color_mask, (5, 5), 0)

            #define a kerneal for opening, closing, blur
            kernel = np.ones((9, 9), np.uint8)

            opening = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

            smoothed_mask = cv2.GaussianBlur(closing, (9, 9), 0)

            blue_image = cv2.bitwise_and(image, image, mask=smoothed_mask)

            gray_image = blue_image[:, :, 2]

            #circles in binary image
            circles = cv2.HoughCircles(
                gray_image,
                cv2.HOUGH_GRADIENT,
                1,
                5,
                param1=200,
                param2=20,
                minRadius=5,
                maxRadius=100
            )

            # check if we found a ball, if so show it and return it
            if circles is not None:
                for c in range(circles.shape[1]):
                    circle = circles[0, c]
                    cords = [circle[0], circle[1]]
                    radius = circle[2]
                    SameBall = False

                    if len(self.memory.lastBallCenters) == 0:
                        self.memory.lastBallCenters.append(cords)
                        self.memory.lastBallColors.append(currentColor)
                        self.memory.lastballsCount +=1
                        self.memory.lassBallRadius.append(radius)

                    else:
                        for i in range(len(self.memory.lastBallCenters)):
                            cord = self.memory.lastBallCenters[i]
                            if abs(cords[0]-cord[0]) < radius*1.5 and abs(cords[1]-cord[1]) < radius*1.5 and radius > 10:
                                SameBall = True

                        if not SameBall:
                            self.memory.lastBallCenters.append(cords)
                            self.memory.lastBallColors.append(currentColor)
                            self.memory.lastballsCount += 1
                            self.memory.lassBallRadius.append(radius)

        #check if camera is ready again
        if cv2.waitKey(33) == 27:
            self.memory.camera.videoProxy.unsubscribe(self.memory.camera.cam)
        return True


class Gaze:
    def __init__(self, memory):
        self.memory = memory

        self.matlabEngine = matlab.engine.start_matlab()

        # add the gaze_follow folder to the matlab path
        # base_path = r'/home/tjalling/Desktop/ru/DevRob/'
        # gaze_follow_path = base_path + r'gaze_follow_model'
        # eng.addpath(gaze_follow_path,nargout=0)


    def getGaze(self):
        # -------------------------------
        # find the gaze of the given centered person
        # -------------------------------

        # save image of Naos camera
        self.memory.camera.getImg(saveImg=True)

        # get the coordinates of the eye
        if self.memory.eye is False:
            return False

        [x, y] = self.memory.eye
        x = int(x)
        y = int(y)

        # call the follow_gaze function in matlab with the x,y coordinates
        matlabShit = self.matlabEngine.follow_gaze(x, y)

        # convert from matlab.double to python list
        c = []
        for _ in range(matlabShit.size[1]):
            c.append(matlabShit._data[_*matlabShit.size[0]:_*matlabShit.size[0]+matlabShit.size[0]].tolist())
        self.memory.gazeVector = [c[0][0], c[1][0], c[2][0], c[3][0]]
        return True


    def quitMatlab(self):
        # -------------------------------
        # shut down of matlab when the robot shutdown or crashed
        # -------------------------------

        self.matlabEngine.quit()

class Face:
    def __init__(self, memory):
        self.memory = memory
        self.faceCoords = []
        self.eye = False
        self.faceCentered = False

    def getEyes(self, camera, leftEyeDet, rightEyeDet):
        #-------------------------------
        # get an eye coordinate, we only need one
        # The coordinate of the eye is relative from the face rectangle, so add
        # the coordinates from the face rectangle
        #-------------------------------

        #check if left and else if right eye has a coord, if so get the eye coords which we need for gaze detection
        if leftEyeDet != []:
            leftEyeCoords = camera.getCenter(leftEyeDet, 0)
            leftEyeCoords = [leftEyeCoords[0] + self.memory.faceUpperLeft[0], leftEyeCoords[1] + self.memory.faceUpperLeft[1]]
            self.eye = leftEyeCoords
            print "Using left eye"
        elif rightEyeDet != []:
            rightEyeCoords = camera.getCenter(rightEyeDet, 0)
            rightEyeCoords = [rightEyeCoords[0] + self.memory.faceUpperLeft[0], rightEyeCoords[1] + self.memory.faceUpperLeft[1]]
            self.eye = rightEyeCoords
            print "Using right eye"
        return True


    def checkEyeContact(self):
        #-------------------------------
        #check if there is eyecontact between the person and the robot
        #-------------------------------

        gazeVector = self.memory.gazeVector
        faceCentered = self.memory.faceCentered

        rangeX = self.memory.camera.rangeX
        rangeY = self.memory.camera.rangeY
        print ("rangeX:", rangeX, " rangeY:", rangeY)

        #checking if the gaze starts and ends within 10% of the camera center, if so we have eye contact
        if faceCentered == True and gazeVector[2] < rangeX[1] and gazeVector[2] > rangeX[0] and gazeVector[3] < rangeY[1] and gazeVector[3] > rangeY[0]:
            self.memory.havingEyeContact = True
        else:
            self.memory.havingEyeContact = False

        return True



    def determineIfCentered(self, camera):
        #-------------------------------
        # check if the face is in the center of camera
        #-------------------------------

        if self.faceCoords[0] > camera.rangeX[0] and self.faceCoords[0] < camera.rangeX[1] and self.faceCoords[1] > \
                camera.rangeY[0] and self.faceCoords[1] < camera.rangeY[1]:
            self.faceCentered = True
        return True

    def getFace(self):

        camera = self.memory.camera
        self.faceCoords = []
        self.faceCentered = False

        #loop 3 times to get a more robost face found
        face = []
        leftEye = []
        rightEye = []
        distToCenter = 100000
        for i in range(3):
            image = camera.getImg()
            if cv2.waitKey(33) == 27:
                camera.videoProxy.unsubscribe(camera.cam)

            #if there was an image captured
            if image is not False:
                #get the face coordinates
                faceDet, leftEyeDet, rightEyeDet = camera.findFace(image)
                #check if there is a face
                if faceDet != []:
                    #get the center of the face
                    faceCent = camera.getCenter(faceDet, 0)
                    #dist from the camera center to the face
                    dist = np.sqrt( ((faceCent[0] - camera.center[0])**2) + ((faceCent[1] - camera.center[1])**2))
                    #if the face is the closest to the camera center save it
                    if dist < distToCenter:
                        distToCenter = dist
                        face = faceDet
                        leftEye = leftEyeDet
                        rightEye = rightEyeDet
                #sleep a bit so that an difference can occur
                sleep(0.1)

        # check if we found a face, and if so if we found an eye
        if face != []:
            self.faceCoords = camera.getCenter(face, 0)
            self.memory.faceUpperLeft = [face[0][0], face[0][1]]
            self.determineIfCentered(camera)
            self.getEyes(camera, leftEye, rightEye)
        else:
            self.memory.face = []
            self.memory.eye = []
            self.memory.faceCentered = []

        self.memory.face = self.faceCoords
        self.memory.eye = self.eye

        self.memory.faceCentered = self.faceCentered
