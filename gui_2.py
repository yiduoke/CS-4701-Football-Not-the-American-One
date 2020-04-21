import gym
import gym_futbol
import baseline_implementation as training

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
    
    
# Return x in (x,y)
def x_coor(coors):
    return coors[0]

# Return y in (x,y)
def y_coor(coors):
    return coors[1]

# take one step in the game
def players_step():
    global observation
    global action
    
    observation2, reward, done, info = environment.step(action)
    
    
    observation = observation2
    for i in range(num_players):
        players[i] = [observation[0,i,0], observation[0,i,1]]
    ball_coors = [observation[0,-1,0], observation[0,-1,1]]
    action2, _states = model.predict(observation)
    
    action = action2
    

def init():
    print("startinggggggg\n\n\n\n")
    # dimensions of the football field
    ax.set_xlim(0, 1050)
    ax.set_ylim(0, 680)
    
    for i in range(num_players):
        players.append([200,200])
        
    ball_coors.append(500)
    ball_coors.append(500)
    return field,

def animate(i):
    """perform animation step"""
    players_step()
    xdata = [] # need these wipes so we don't get 2938724 balls on the screen
    ydata = []
    xdata = list(map(x_coor, players))
    ydata = list(map(y_coor, players))
    
    xdata.append(ball_coors[0])
    ydata.append(ball_coors[1])
    
#    plt.plot(xdata[:-1], ydata[:-1], 'ro') # players are red
#    plt.plot(xdata[-1], ydata[-1], 'go') # ball is green
    time.sleep(0.05)
    field.set_data(xdata, ydata)
    return field,
        

ani = animation.FuncAnimation(fig, animate, frames=600,
                              interval=10, blit=True, init_func=init)


# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
#ani.save('particle_box.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
plt.show()
