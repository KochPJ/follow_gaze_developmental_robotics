### follow_gaze_developmental_robotics
follow gaze for nao robot using matcaffe opencv and reinforcement learning


### Installation
- Install the dependencies listed below
- Clone or download this project
- Setup as listed below

#### Dependencies
The code is writen for pyhton 2.7. Futher dependencies are:
- gym 0.10.5
- numpy 1.14.5
- opencv-python 3.4.1.15
- pandas 0.23.1
- matplotlib 2.2.2
- naoqi
- matlabengineforpython
- matcaffe
Note that the given version were used during development however, other version might also work.

#### Setup of code
In order to run the gaze following with matcaffe, you need to add the path to your matcaffe folder in `follow_gaze.m` and `predict_gaze.m`:  
E.g. add: `addpath(genpath('/path/to/your/caffe/matlab'));`.

Also change the ip variable on line 21 of `Pipeline.py` to the ip of your nao robot.  
Then run `python Pipeline.py`.



### Run the code

The following step

You can run the code by running Pipeline.py. However, before running you need to set some path and the robot IP.
In Pipeline.py set the ip in line 21 to the ip of your nao robot.
In order to run the gaze following with matcaffe you need to add the path to your matcaffe the follow_gaze.m .
Add: addpath(genpath('/path/to/your/caffe/matlab'));
Also add the same path to the predict_gaze.m .
After both paths to matcaffe have been set in the follow_gaze.m and the predict_gaze.m file you can run the
code with Pipeline.py.  



### Architecture
![Architecture](https://github.com/KochPJ/follow_gaze_developmental_robotics/blob/master/architecture.png  "Architecture")


We used object oriented programming for coding the follow_gaze project. We got the following classes:
- Memory
- Decision
- Learning
- Motivation
- Perception
  - Camera
  - Ball
  - Face
  - Gaze
- Motorcontroll

The pipeline is handling each object instance of these clases. The camera is setup first.
The memory then inherent the camera. And the remaining classes are then inharenting the memory. Thereby, each class can use the camera and get an image. Furtermore, all classes can communicate over the memory, where all variables are stored. The pipeline calles the functions of the created objects. Every function is run by the pipeline. Inside the pipeline it starts out by initializing and setup the robot proxies and objects. Afterwards, the main loop starts where the main pipeline is executed. The loop executes in the following algorithm:
- setup the current run
- while the run is not done do:
  - get a face in the image
  - get the balls in the image
  - get the motivation of the robot
  - make a decision based on the motivation
  - execute the decision
- safe learnings to a csv file (long term memory)
- waiting for terminal input instructions (continue new trial, or shutdown)
