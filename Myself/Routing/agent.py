import tensorflow as tf
import numpy as np

from tensorflow.keras import optimizers, losses
from tensorflow.keras import Model
from collections import deque

import random



class DQN(Model):
    def __init__(self):
        super(DQN, self).__init__()
        self.layer1 = tf.keras.layers.Dense(64, activation='relu')
        self.layer2 = tf.keras.layers.Dense(64, activation='relu')
        self.layer3 = tf.keras.layers.Dense(64, activation='relu')
        self.layer4 = tf.keras.layers.Flatten()
        self.value = tf.keras.layers.Dense(20)

    def call(self, state):
        layer1 = self.layer1(state)
        layer2 = self.layer2(layer1)
        layer3 = self.layer3(layer2)
        layer4 = self.layer4(layer3)
        value = self.value(layer4)
        return value

class Agent:
    def __init__(self):
        # hyper parameters
        self.lr = 0.01
        self.gamma = 0.9

        self.dqn_model = DQN()
        self.dqn_target = DQN()
        
        self.opt = optimizers.Adam(lr=self.lr, )

        self.batch_size = 64
        self.action_size = 20

        self.memory = deque(maxlen=1000)

    def update_target(self):
        self.dqn_target.set_weights(self.dqn_model.get_weights())

    def get_action(self, state, epsilon):
        q_value = self.dqn_model(tf.convert_to_tensor(state, dtype=tf.float32))[0]
        if np.random.rand() <= epsilon:
           # print("random")
            action = np.random.choice(self.action_size)
        else:
           # print("greedy")
            action = np.argmax(q_value) 
        return action, q_value

    def append_sample(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))

    def save_model(self,i,j):
        tf.saved_model.save(self.dqn_model,"model/"+str(i)+"_"+str(j))

    def update(self):
        mini_batch = random.sample(self.memory, self.batch_size)

        states = [i[0] for i in mini_batch]
        actions = [i[1] for i in mini_batch]
        next_states = [i[2] for i in mini_batch]
        rewards = [i[3] for i in mini_batch]

        dqn_variable = self.dqn_model.trainable_variables

        with tf.GradientTape() as tape:
            tape.watch(dqn_variable)
            
            rewards = tf.convert_to_tensor(rewards, dtype=tf.float32)

            actions = tf.convert_to_tensor(actions, dtype=tf.int32)
            
            target_q = self.dqn_target(tf.convert_to_tensor(next_states))
            next_action = tf.argmax(target_q, axis=1)
            target_value = tf.reduce_sum(tf.one_hot(next_action, self.action_size) * target_q, axis=1)
            target_value = self.gamma * target_value + rewards
            main_q = self.dqn_model(tf.convert_to_tensor(states, dtype=tf.float32))
            main_value = tf.reduce_sum(tf.one_hot(actions, self.action_size) * main_q, axis=1)
            error = tf.losses.mean_squared_error(main_value, target_value)

        dqn_grads = tape.gradient(error, dqn_variable)
        self.opt.apply_gradients(zip(dqn_grads, dqn_variable))
