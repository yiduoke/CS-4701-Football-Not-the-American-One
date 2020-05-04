# -*- coding: utf-8 -*-
"""Copy of Two_player_training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WBmPbBLLN_jQcP5p1vN2JzeX7FsT6Sav

https://github.com/higgsfield/RL-Adventure-2
"""

"""# env"""

import gym
import gym_futbol

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/gym-futbol/gym_futbol/envs/

futbol_env = gym.make("Futbol-v0")

futbol_env.step(15)

"""# A2C

## import
"""

import math
import random

import gym
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical

# Commented out IPython magic to ensure Python compatibility.
from IPython.display import clear_output
import matplotlib.pyplot as plt
# %matplotlib inline
from IPython import display

"""## Use CUDA"""

use_cuda = torch.cuda.is_available()
device   = torch.device("cuda" if use_cuda else "cpu")

device

"""## Environments and Worker class"""

#This code is from openai baseline
#https://github.com/openai/baselines/tree/master/baselines/common/vec_env

import numpy as np
from multiprocessing import Process, Pipe

def worker(remote, parent_remote, env_fn_wrapper):
    parent_remote.close()
    env = env_fn_wrapper.x()
    while True:
        cmd, data = remote.recv()
        if cmd == 'step':
            ob, reward, done, info = env.step(data)
            if done:
                ob = env.reset()
            remote.send((ob, reward, done, info))
        elif cmd == 'reset':
            ob = env.reset()
            remote.send(ob)
        elif cmd == 'reset_task':
            ob = env.reset_task()
            remote.send(ob)
        elif cmd == 'close':
            remote.close()
            break
        elif cmd == 'get_spaces':
            remote.send((env.observation_space, env.action_space))
        else:
            raise NotImplementedError

class VecEnv(object):
    """
    An abstract asynchronous, vectorized environment.
    """
    def __init__(self, num_envs, observation_space, action_space):
        self.num_envs = num_envs
        self.observation_space = observation_space
        self.action_space = action_space

    def reset(self):
        """
        Reset all the environments and return an array of
        observations, or a tuple of observation arrays.
        If step_async is still doing work, that work will
        be cancelled and step_wait() should not be called
        until step_async() is invoked again.
        """
        pass

    def step_async(self, actions):
        """
        Tell all the environments to start taking a step
        with the given actions.
        Call step_wait() to get the results of the step.
        You should not call this if a step_async run is
        already pending.
        """
        pass

    def step_wait(self):
        """
        Wait for the step taken with step_async().
        Returns (obs, rews, dones, infos):
         - obs: an array of observations, or a tuple of
                arrays of observations.
         - rews: an array of rewards
         - dones: an array of "episode done" booleans
         - infos: a sequence of info objects
        """
        pass

    def close(self):
        """
        Clean up the environments' resources.
        """
        pass

    def step(self, actions):
        self.step_async(actions)
        return self.step_wait()

    
class CloudpickleWrapper(object):
    """
    Uses cloudpickle to serialize contents (otherwise multiprocessing tries to use pickle)
    """
    def __init__(self, x):
        self.x = x
    def __getstate__(self):
        import cloudpickle
        return cloudpickle.dumps(self.x)
    def __setstate__(self, ob):
        import pickle
        self.x = pickle.loads(ob)

        
class SubprocVecEnv(VecEnv):
    def __init__(self, env_fns, spaces=None):
        """
        envs: list of gym environments to run in subprocesses
        """
        self.waiting = False
        self.closed = False
        nenvs = len(env_fns)
        self.nenvs = nenvs
        self.remotes, self.work_remotes = zip(*[Pipe() for _ in range(nenvs)])
        self.ps = [Process(target=worker, args=(work_remote, remote, CloudpickleWrapper(env_fn)))
            for (work_remote, remote, env_fn) in zip(self.work_remotes, self.remotes, env_fns)]
        for p in self.ps:
            p.daemon = True # if the main process crashes, we should not cause things to hang
            p.start()
        for remote in self.work_remotes:
            remote.close()

        self.remotes[0].send(('get_spaces', None))
        observation_space, action_space = self.remotes[0].recv()
        VecEnv.__init__(self, len(env_fns), observation_space, action_space)

    def step_async(self, actions):
        for remote, action in zip(self.remotes, actions):
            remote.send(('step', action))
        self.waiting = True

    def step_wait(self):
        results = [remote.recv() for remote in self.remotes]
        self.waiting = False
        obs, rews, dones, infos = zip(*results)
        return np.stack(obs), np.stack(rews), np.stack(dones), infos

    def reset(self):
        for remote in self.remotes:
            remote.send(('reset', None))
        return np.stack([remote.recv() for remote in self.remotes])

    def reset_task(self):
        for remote in self.remotes:
            remote.send(('reset_task', None))
        return np.stack([remote.recv() for remote in self.remotes])

    def close(self):
        if self.closed:
            return
        if self.waiting:
            for remote in self.remotes:            
                remote.recv()
        for remote in self.remotes:
            remote.send(('close', None))
        for p in self.ps:
            p.join()
            self.closed = True
            
    def __len__(self):
        return self.nenvs

"""## Neural Network"""

class ActorCritic(nn.Module):
    def __init__(self, num_inputs, num_outputs, hidden_size, std=0.0):
        super(ActorCritic, self).__init__()
        
        self.critic = nn.Sequential(
            nn.Linear(num_inputs, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )
        
        self.actor = nn.Sequential(
            nn.Linear(num_inputs, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, num_outputs),
            nn.Softmax(dim=1),
        )
        
    def forward(self, x):
        value = self.critic(x)
        probs = self.actor(x)
        dist  = Categorical(probs)
        return dist, value

"""# Training Function"""

def plot(frame_idx, rewards):
    clear_output(True)
    plt.figure(figsize=(20,5))
    plt.subplot(131)
    plt.title('frame %s. reward: %s' % (frame_idx, rewards[-1]))
    plt.plot(rewards)
    plt.show()

def get_action_str(action):
      if action == 0:
            action_str = "run"
      elif action == 1:
            action_str = "intercept"
      elif action == 2:
            action_str = "shoot"
      else:
            action_str = "assist"

      return action_str

def test_env(env, num_inputs, model, vis=False):
    state = env.reset()
    state = np.reshape(state, [1, num_inputs])
    if vis: env.render()
    done = False
    total_reward = 0
    while not done:
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        dist, _ = model(state)
        action = dist.sample().cpu().numpy()[0]
        next_state, reward, done, _ = env.step(action)
        next_state = np.reshape(next_state, [1, num_inputs])
        state = next_state

        if vis: 

              plt.clf()

              individual_size = 4

              predicition_ai1_action_type = action // individual_size 
              predicition_ai2_action_type = action % individual_size  

              title_str = ("reward : " + str(reward)
                          + "\n ai 1 action : " + get_action_str(predicition_ai1_action_type)
                          + "\n ai 2 action : " + get_action_str(predicition_ai2_action_type)
                          )
              plt.xlim(0, env.length)
              plt.ylim(0, env.width)

              # ai
              ai_1_x, ai_1_y, _, _, _ = env.obs[env.ai_1_index]
              ai_2_x, ai_2_y, _, _, _ = env.obs[env.ai_2_index]
              plt.plot(ai_1_x,ai_1_y, color = 'red', marker='o', markersize=10, label='ai1')
              plt.plot(ai_2_x,ai_2_y, color = 'red', marker='o', markersize=10, label='ai2')

              # opp_1
              opp_1_x, opp_1_y, _, _, _ = env.obs[env.opp_1_index]
              opp_2_x, opp_2_y, _, _, _ = env.obs[env.opp_2_index]
              plt.plot(opp_1_x, opp_1_y, color = 'blue', marker='o', markersize=10, label='opp1')
              plt.plot(opp_2_x, opp_2_y, color = 'blue', marker='o', markersize=10, label='opp2')
              # ball
              ball_x, ball_y, _, _, _ = env.obs[env.ball_index]
              plt.plot(ball_x, ball_y, color = 'green', marker='o', markersize=6, label='ball')

              plt.legend()

              plt.title(title_str, loc = 'left')

              display.display(plt.gcf())
              display.clear_output(wait=True)

        total_reward += reward

    return total_reward

def compute_returns(next_value, rewards, masks, gamma=0.99):
    R = next_value
    returns = []
    for step in reversed(range(len(rewards))):
        R = rewards[step] + gamma * R * masks[step]
        returns.insert(0, R)
    return returns

def train_model(env, envs, num_inputs, num_envs, model, optimizer, max_frames = 20000):
      
      frame_idx    = 0
      test_rewards = []
      
      state = envs.reset()
      state = np.reshape(state, [num_envs, num_inputs])

      while frame_idx < max_frames:

          log_probs = []
          values    = []
          rewards   = []
          masks     = []
          entropy = 0

          for _ in range(num_steps):

              state = torch.FloatTensor(state).to(device)
              
              dist, value = model(state)

              action = dist.sample()
              next_state, reward, done, _ = envs.step(action.cpu().numpy())
              next_state = np.reshape(next_state, [num_envs, num_inputs])

              log_prob = dist.log_prob(action)
              entropy += dist.entropy().mean()
              
              log_probs.append(log_prob)
              values.append(value)
              rewards.append(torch.FloatTensor(reward).unsqueeze(1).to(device))
              masks.append(torch.FloatTensor(1 - done).unsqueeze(1).to(device))
              
              state = next_state
              
              if frame_idx % 1000 == 0:
                  test_rewards.append(np.mean([test_env(env, num_inputs, model) for _ in range(10)]))
#                  plot(frame_idx, test_rewards) # helper

              frame_idx += 1
                  
          next_state = torch.FloatTensor(next_state).to(device)

          _, next_value = model(next_state)
          returns = compute_returns(next_value, rewards, masks) # helper
          
          log_probs = torch.cat(log_probs)
          returns   = torch.cat(returns).detach()
          values    = torch.cat(values)

          advantage = returns - values

          actor_loss  = -(log_probs * advantage.detach()).mean()
          critic_loss = advantage.pow(2).mean()

          loss = actor_loss + 0.5 * critic_loss - 0.001 * entropy

          optimizer.zero_grad()
          loss.backward()
          optimizer.step()

"""# Training"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/gym-futbol/gym_futbol/envs/

# from common.multiprocessing_env import SubprocVecEnv

num_envs = 16
env_name = "Futbol-v0"

def make_env():
    def _thunk():
        env = gym.make(env_name)
        return env

    return _thunk

futbol_envs = [make_env() for i in range(num_envs)]
futbol_envs = SubprocVecEnv(futbol_envs)

futbol_env = gym.make(env_name)

state_size_a, state_size_b = futbol_env.observation_space.shape
num_inputs = state_size_a * state_size_b
num_outputs = 16

#Hyper params:
hidden_size = 256
lr          = 3e-4
num_steps   = 5

futbol_model = ActorCritic(num_inputs, num_outputs, hidden_size).to(device)
futbol_optimizer = optim.Adam(futbol_model.parameters())

train_model(futbol_env, futbol_envs, num_inputs, num_envs, futbol_model, futbol_optimizer, max_frames = 20000000)

total_reward = test_env(futbol_env, num_inputs, futbol_model, vis=True)