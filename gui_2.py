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

players = [] # holds players' coordinates; only 2 right now
num_players = 2
environment = training.env
observation = environment.reset()
model = training.model
action, _states = model.predict(observation)

def init():
    # dimensions of the football field
    ax.set_xlim(0, 1050)
    ax.set_ylim(0, 680)
    for i in range(num_players):
        players.append([random.random() * 1050, random.random() * 680])
    return field,
    
    
# Return x in (x,y)
def x_coor(coors):
    return coors[0]

# Return y in (x,y)
def y_coor(coors):
    return coors[1]

# take one step in the game
def players_step():
    observation2, reward, done, info = environment.step(action)
    observation = observation2
    print(observation)
    for i in range(num_players):
        players[i][0] = observation[0,i,0]
        players[i][1] = observation[0,i,1]

def animate(i):
    """perform animation step"""
    players_step()
    time.sleep(0.1) # wait for one second
    xdata = list(map(x_coor, players))
    ydata = list(map(y_coor, players))
#    field.set_data(map(x_coor, players), map(y_coor, players)) # map (higher order function)
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
