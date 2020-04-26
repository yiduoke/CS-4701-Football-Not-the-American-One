
import gym
import gym_futbol
import baseline_implementation as training
from IPython import display

import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import matplotlib.animation as animation
import random
import time

###### run this file AFTER training

fig, ax = plt.subplots()
xdata, ydata = [], []
field, = plt.plot([], [], 'ro')

players = [] # holds players' coordinates; only 2 players right now
ball_coors = [] # doesn't matter, but has to be length 2
num_players = 2
environment = training.env
#global observation
observation = environment.reset()
model = training.model
#global action
action, _states = model.predict(observation)
#global done
done = False

field_width = 105
field_length = 68
    
    
# Return x in (x,y)
#def x_coor(coors):
#    return coors[0]
#
## Return y in (x,y)
#def y_coor(coors):
#    return coors[1]
#
## take one step in the game
#def players_step():
#    global observation
#    global action
#
#    observation, reward, done, info = environment.step(action)
#
#    for i in range(num_players):
#        players[i] = [observation[0,i,0], observation[0,i,1]]
#    ball_coors = [observation[0,-1,0], observation[0,-1,1]]
#    action, _states = model.predict(observation)
    
    

#def init():
#    print("startinggggggg\n\n\n\n")
#    # dimensions of the football field
#    ax.set_xlim(0, field_width)
#    ax.set_ylim(0, field_length)
#
#    for i in range(num_players):
#        players.append([observation[0,i,0], observation[0,i,1]])
#
#    ball_coors.append(observation[0,-1,0])
#    ball_coors.append(observation[0,-1,1])
#
#def animate(i):
#    """perform animation step"""
#    players_step()
#    xdata = [] # need these wipes so we don't get 2938724 balls on the screen
#    ydata = []
#    xdata = list(map(x_coor, players))
#    ydata = list(map(y_coor, players))
#
#    xdata.append(ball_coors[0])
#    ydata.append(ball_coors[1])
#    print(xdata)
#    print(ydata)
    
#    plt.plot(xdata[:-1], ydata[:-1], 'ro') # players are red
#    plt.plot(xdata[-1], ydata[-1], 'go') # ball is green
#    time.sleep(0.05)
#    field.set_data(xdata, ydata)
#    return field,
     
     
     
done = False

#animation loop
while not done:
#    global observation
#    global done
#    global action
    
    # stepping the environment
    action, _states = model.predict(observation)
    observation, reward, done, info = environment.step(action)
    
    # animation
    plt.clf()
    
    plt.xlim(0, field_length)
    plt.ylim(0, field_width)

    # team 1
    for i in range(num_players//2):
        plt.plot(observation[0,i,0], observation[0,i,1], color = 'red', marker = 'o', markersize = 12, label = 'team 1')
    
    # team 2
    for j in range(num_players//2, num_players):
        plt.plot(observation[0,j,0], observation[0,j,1], color = 'blue', marker = 'o', markersize = 12, label = 'team 1')
    
    # ball
    plt.plot(observation[0,-1,0], observation[0,-1,1], color = 'green', marker = 'o', markersize = '8', label = 'ball')
    
    plt.legend()
    display.display(plt.gcf())
    display.clear_output(wait=True)
    
