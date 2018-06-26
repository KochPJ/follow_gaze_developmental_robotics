import numpy as np
import Perception
import Decision
import Memory
import random
import gym
import Learning
import math
import naoenvSimulation
import matplotlib.pyplot as plt


camera = Perception.Camera()
memory = Memory.Memory(camera)
Perc = Perception.Ball(memory)
learning = Learning.Learning(memory)
Dec = Decision.Decision(memory,learning)

def createEnvironment(numberOfPossibleBalls, environment, center):
    #create some balls
    ball = [0,0]
    gaze = [0,0]
    while gaze[0] == 0 or gaze[1] == 0:
        ball[0] = random.randrange(environment[0], environment[1], 1)
        ball[1] = random.randrange(environment[2], environment[3], 1)
        #create the gaze
        gaze = [ball[0]-center[0], ball[1]-center[1]]

    #find the direction of the gaze
    directionx = 1
    directiony = 1
    limx = environment[1]
    limy = environment[3]
    if gaze[0] > center[0]:
        directionx = 1
        limx = environment[1]
    else:
        directionx = -1
        limx = environment[0]

    if gaze[1] > center[1]:
        directiony = 1
        limy = environment[3]
    else:
        directiony = -1
        limy = environment[2]

    balls = []
    for pb in range(numberOfPossibleBalls):
        ballInEnvironment = False
        posyatx = 0
        x = 0
        while ballInEnvironment != True:
            x = random.randrange(center[0], limx, directionx)
            gradient = float(gaze[1])/float(gaze[0])
            posyatx = center[1] + int(gradient * x)
            if posyatx > 1600 or posyatx < 400:
                limx = x
            else:
                ballInEnvironment = True

        p = random.random()
        if p < 0.5:
            y = random.randrange(posyatx+100, posyatx+400, 1)
        else:
            y = random.randrange(posyatx-100, posyatx-400, -1)

        balls.append([x, y])
    return ball, balls, gaze


def moveImage(action, gaze, currentPos, increment = 250):
    x = 0
    y = 0
    if action == "Followgaze":
        direction = 1
        if gaze[0] <= 0:
            direction = -1

        gradient = float(gaze[1]) / float(gaze[0])
        distPerx = np.sqrt( 1 + (gradient**2) )
        move_in_x = (float(increment) / distPerx)* direction
        x = currentPos[0] + int(move_in_x)
      #  in_x = int(move_in_x * direction)
       # move_in_y = gradient * move_in_x
        y = currentPos[1] + int(gradient * move_in_x)

       # in_y = int(gradient * move_in_x)
     #   distxy = np.sqrt(( (abs(in_x)**2) + (abs(in_y)*+2)))

    elif action == "left":
        x = currentPos[0] + increment
        y = currentPos[1]
    elif action == "right":
        x = currentPos[0] - increment
        y = currentPos[1]
    else:
        print("not an action")
    return [x, y]


def getItemsInImage(image, currentPos, balls):
    currentBalls = []
    nofBalls = sum(np.array(balls).shape)
    #print(nofBalls)
    if nofBalls > 2:
        for b in balls:
            if b[0] < currentPos[0]+image[0] and b[0] > currentPos[0]-image[0] and b[1] < currentPos[1]+image[1] and b[1] > currentPos[1]- image[1]:
                currentBalls.append(b)
    elif nofBalls == 2:
        if balls[0] < currentPos[0] + image[0] and balls[0] > currentPos[0] - image[0] and balls[1] < currentPos[1] + image[1] and balls[1] > currentPos[1] - image[1]:
            currentBalls.append(balls)
    return currentBalls


def decision(probability):
    return random.random() < probability

def getAction(q_table, possibleActions, eps, s):

    # get the best available action with the highest associated Q value
    bestAvailableAction = -1
    bestQValue = 0
    for possibleAction in possibleActions:
        qValue = q_table[s, possibleAction-1]

        if bestAvailableAction == -1 or qValue > bestQValue:
            bestAvailableAction = possibleAction
            bestQValue = qValue

    a = bestAvailableAction

    # sometimes do a random action (eps) or if there are no q_values yet
    if np.random.random() < eps or np.sum(q_table[s, :]) == 0:
        a = random.choice(possibleActions)

    return a


def getPossibleActions(state, distances, currentPos):
    possibleActions = []
    if state == 0:
        possibleActions = [1,2,3]
        return possibleActions

    if currentPos[0] >  -700 and currentPos[0] < 700 and currentPos[1] < 1700 and currentPos[1]> 300 :
        possibleActions.append(state)
    else:
        possibleActions.append(6)
        return possibleActions

    if state not in [1, 2, 3]:
        print("error in get action: action state not 1,2, or 3")
        possibleActions.append(6)
        return possibleActions

    #threshold is the middle point between resolution x and y (640 and 420 t = 530*0.1 = 53) 10% of the middle
    threshold = 100
    faraway = False
    closeby = False
    for dist in distances:
        if dist < threshold:
            closeby = True
        else:
            faraway = True

    if closeby:
        possibleActions.append(4)
    if faraway:
        possibleActions.append(5)
    if possibleActions == []:
        possibleActions.append(6)

    return possibleActions

def doActions(a, g, currentPos, distances, bs):

    reValues = [a,0]
    if a == 1:
        reValues[1] = moveImage("left", g, currentPos)
    elif a == 2:
        reValues[1] = moveImage("right", g, currentPos)
    elif a == 3:
        reValues[1] = moveImage("Followgaze", g, currentPos)
    elif a == 4:
        reValues[1] = bs[distances.index(min(distances))]
    elif a == 5:
        reValues[1] = bs[distances.index(max(distances))]

    return reValues

def distToVec(Vec, ballCenters):
    VecStart = np.array([Vec[0],Vec[1]])
    VecEnd = np.array([Vec[2], Vec[3]])
    length = sum(np.array(ballCenters).shape)
    if length > 2:
        dist = []
        for ballCent in ballCenters:
            #print(VecStart, VecEnd ,np.array(ballCent) )
            d = np.linalg.norm(np.cross(VecEnd-VecStart, VecStart - np.array(ballCent)))/ np.linalg.norm(VecEnd-VecStart)
            dist.append(d)
    elif length == 2:
        dist = np.linalg.norm(np.cross(VecEnd-VecStart, VecStart - np.array(ballCenters)))/ np.linalg.norm(VecEnd-VecStart)
    else:
        dist = []

    return dist

def f_value(old_q, new_q, sigma):
    return (1.0 - math.exp(-abs(new_q - old_q)/sigma))/(1.0 + math.exp(-abs(old_q - new_q)/sigma))


def Simulation(numberOfMaxIterations, considerLastN, betterThen, resetQtable_after_x_iterations,y = 0.8, lr = 0.2):
    #initial variables
    e = [-1000, 1000, 0, 2000] # x to x and y to y environment
    c = [0,1000] # xy center
    image = [500,500] # image size

    env = gym.make('NaoEnvSim-v0')

    q_table = np.zeros((env.states, env.actions))

    epsilons = np.ones(4)
    delta = 0.05
    sigma = 20.0  # Experimental

    correctBallFoundList = []
    GoodEnough = False
    GoodEnough_at = 0
    countIteraction = 0
    resetCounter = 0
    while not GoodEnough and countIteraction < numberOfMaxIterations:


        #create a new environment
        numberOfBalls = random.choice([0,1,2,3,4,5])
        b, bs, g = createEnvironment(numberOfBalls, e, c)
        gazeVec = [c[0], c[1], c[0] + g[0], c[1] + g[1]]
        bs.append(b)  # add the gaze ball to the list of all balls
        currentPos = [0, 1000]  # reset current position to center
        s = 0

        done = False
        stateHistory = []
        positionHistory = []
        actionHistory = []
        counter = 0
        correctBallFound = False
        lastNmean = 0
        while not done and counter < 20:
            eps = epsilons[s]
            stateHistory.append(s)
            positionHistory.append(currentPos)
            counter += 1
            currentBalls = getItemsInImage(image, currentPos, bs)
            distances = distToVec(gazeVec, currentBalls)
            possibleActions = getPossibleActions(s, distances, currentPos)
            a = getAction(q_table, possibleActions, eps, s)
            actionHistory.append(a)
            ActionDone = doActions(a, g, currentPos, distances, bs)

            correctBallFound = False
            if ActionDone[0] == 1 or ActionDone[0] == 2 or ActionDone[0] == 3:
                currentPos = ActionDone[1]

            elif ActionDone[0] == 4 or ActionDone[0]==5:
                ball = ActionDone[1]
                offset = 50
                if ball[0] < b[0]+offset and ball[0] > b[0]-offset and ball[1] < b[1]+offset and ball[1] > b[1]-offset:
                    correctBallFound = True

            new_s, r, done, _ = env.step(a, correctBallFound)

            old_q = q_table[s, a - 1]
            q_table[s, a - 1] = (1 - lr) * q_table[s, a - 1] + lr * (r + y * np.max(q_table[new_s, :]))
            new_q = q_table[s, a - 1]

            epsilons[s] = delta * f_value(old_q, new_q, sigma) + (1.0 - delta) * epsilons[s]

            s = new_s

        correctBallFoundList.append(correctBallFound)
        if countIteraction > considerLastN:
            lastN = np.array(correctBallFoundList[-considerLastN:]).astype('int')
            lastNmean = np.mean(lastN)
            if lastNmean > betterThen:
                GoodEnough_at = countIteraction
                GoodEnough = True

        if resetCounter == resetQtable_after_x_iterations:
            resetCounter = 0
            q_table = np.zeros((env.states, env.actions))



        resetCounter += 1
        countIteraction += 1

    return GoodEnough, GoodEnough_at, correctBallFoundList, epsilons, q_table
Result = False
while not Result:
    Result, GoodAt, correctBallFoundList, eps, q_table= Simulation(500, 20, 0.90, 500)
    print(Result, GoodAt, np.mean(np.array(correctBallFoundList).astype(int)[GoodAt:]), eps)
    Result = True

print(Result, GoodAt, np.mean(np.array(correctBallFoundList).astype(int)[GoodAt:]), eps)
print(q_table[:-3])
