### follow_gaze_developmental_robotics
follow gaze for nao robot using matcaffe opencv and reinforcement learning


### Installation
download package and extract it to your source. 

### Dependencies
The code is writen for pyhton 2.7. Futher dependencies are:
- gym 0.10.5
- numpy 1.14.5
- opencv-python 3.4.1.15
- pandas 0.23.1
- matplotlib 2.2.2
- naoqi
- matlabengineforpython 
- matcaffe
*note the given version are used for running however, other version might also work.

### Run the code
You can run the code by running Pipeline.py. Howver, before running you need to set some path and the robot IP.
In Pipeline.py set the ip in line 21 to the ip of your nao robot. 
In order to run the gaze following with matcaffe you need to add the path to your matcaffe the follow_gaze.m .
Add: addpath(genpath('/path/to/your/caffe/matlab'));
Also add the same path to the predict_gaze.m .
After both paths to matcaffe have been set in the follow_gaze.m and the predict_gaze.m file you can run the
code with Pipeline.py.  

### Explaining the code
We used object oriented programming for coding the follow_gaze project. We got the following classes:
- Decision
- Learning
- Memory
- Motivation
- Perception
  - Camera
  - Ball
  - Face
  - Gaze
- Motorcontroll
