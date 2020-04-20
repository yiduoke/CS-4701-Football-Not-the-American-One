# Q-learning

# Modified from https://www.learndatasci.com/tutorials/reinforcement-q-learning-scratch-python-openai-gym/

import numpy as np
import random


def qLearning(env, alpha=0.1, gamma=0.6, epsilon=0.1, max_iteration=1000):
    """ Q-learning agent training

          Parameters
          ----------
          env: environment
                  env.reset
                  env.step(action)
                  env.render

          alpha: float
                  Learning rate. Number in range [0, 1]

          gamma: float
                  Discount factor. Number in range [0, 1]

          epsilon: float
                  Exploration factor. Number in range [0, 1]
                  Higher epsilon, more likely to explore the environment

          Returns
          -------
          Q-table: np.ndarray
                  The Q-table learned by the agent.
      """

    q_table = np.zeros([env.observation_space.n, env.action_space.n])

    for i in range(max_iteration):

        state = env.reset()

        epochs, reward, = 0, 0
        done = False

        while not done:
            if random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()  # Explore action space
            else:
                action = np.argmax(q_table[state])  # Exploit learned values

            next_state, reward, done = env.step(action)

            old_value = q_table[state, action]
            next_max = np.max(q_table[next_state])

            new_value = (1 - alpha) * old_value + alpha * \
                (reward + gamma * next_max)
            q_table[state, action] = new_value

            state = next_state
            epochs += 1

        if i % 100 == 0:
            print(f"Episode: {i}")

    print("Training finished.\n")

    return q_table


def qLearningEval(env, q_table, episodes=100):
    """ Q-learning agent evaluation

        Parameters
        ----------
        env: environment
                env.reset
                env.step(action)
                env.render

        Q-table: np.ndarray
                The Q-table learned by the agent.

        epsidoes: int
                  Evaluation epsidoes. 

    """

    total_epochs = 0

    for _ in range(episodes):
        state = env.reset()
        epochs = 0

        done = False

        while not done:
            action = np.argmax(q_table[state])
            state, reward, done = env.step(action)

            epochs += 1

        total_epochs += epochs

    print(f"Results after {episodes} episodes:")
    print(f"Average timesteps per episode: {total_epochs / episodes}")
