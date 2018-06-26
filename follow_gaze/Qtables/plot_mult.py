import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt

df = pd.read_csv("statistics_correct_51.csv")
qtablelist = df["qtable"].values
epsionlist = list(df["epsilon"].values)

q_tables = []
epsilons = []
for i in range(len(qtablelist)):
    qtable_string = qtablelist[i]
    epsilon = epsionlist[i]

    q_table = np.array(list(ast.literal_eval(qtable_string)))[:-3]
    RL_eps = np.array(ast.literal_eval(epsilon))

    q_tables.append(q_table)
    epsilons.append(RL_eps)

q_tables = np.array(q_tables)
epsilons = np.array(epsilons)

print (q_tables.shape)
print (epsilons.shape)
print(q_tables[-1])

Followgaze = q_tables[:,0,2]
left = q_tables[:,0,0]
right = q_tables[:,0,1]

FollowgazeCloseBy = q_tables[:,3,3]
FollowGazeFarAway = q_tables[:,3,4]
FollowGazeContinueLooking = q_tables[:,3,2]

LeftCloseBy = q_tables[:,1,3]
LeftFarAway = q_tables[:,1,4]
LeftContinueLooking = q_tables[:,1,0]

RightCloseBy = q_tables[:,2,3]
RightFarAway = q_tables[:,2,4]
RightContinueLooking = q_tables[:,2,1]

# line1, = plt.plot(epsilons[:,0], label='Eps 0')
# line2, = plt.plot(epsilons[:,1], label='Eps 1')
# line3, = plt.plot(epsilons[:,2], label='Eps 2')
# line4, = plt.plot(epsilons[:,3], label='Eps 3')
# plt.legend(handles=[line1, line2, line3, line4])
# plt.title("Epsilon Probabilities")
# plt.xlabel("Runs")
# plt.ylabel("Probability")
# plt.show()


print ("Plotting start state Q values..")
for i in range(len(Followgaze)):
    plt.clf()
    line1, = plt.plot(Followgaze[0:i], label='Follow Gaze', c=u'#1f77b4')
    line2, = plt.plot(left[0:i], label='Look Left', c=u'#ff7f0e')
    line3, = plt.plot(right[0:i], label='Look Right', c=u'#2ca02c')
    plt.legend(handles=[line1, line2, line3])
    plt.title("Zero State Actions")
    plt.xlabel("Runs")
    plt.ylabel("Qvalue")
    plt.savefig('demo_plots/StartState-' + str(i) + '.png')

# right is 0 als cumulative was always negative

print ("Plotting follow gaze state Q values..")
for i in range(len(Followgaze)):
    plt.clf()
    line1, = plt.plot(FollowgazeCloseBy[0:i], label='Close By', c=u'#1f77b4')
    line2, = plt.plot(FollowGazeFarAway[0:i], label='Far Away', c=u'#ff7f0e')
    line3, = plt.plot(FollowGazeContinueLooking[0:i], label='Continue Looking', c=u'#2ca02c')
    plt.legend(handles=[line1, line2, line3])
    plt.title("FollowGaze")
    plt.xlabel("Runs")
    plt.ylabel("Qvalue")
    plt.savefig('demo_plots/FollowGaze-' + str(i) + '.png')
