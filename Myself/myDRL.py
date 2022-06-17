import sys
sys.path.insert(0,'./Routing')
import agent
import pandas as pd
import numpy as np
import time
import json,ast
import tensorflow as tf
import setting
import copy

SIZE = 24

def DRL_thread():
    print("enter thread")
    column, row = SIZE,SIZE
    brain = [[0]*row for _ in range(column)]
    for i in range(1,SIZE):
        for j in range(1,SIZE):
            if i!=j:
                brain[i][j] =  agent.Agent()

    all_path_list = state_to_action()

    step = 0
    epsilon_ini = 0.1
    epsilon_final = 0.01
    epsilon = 0.1
    action_memory = np.zeros((24,24))
    state_memory = np.zeros((24,24))
    reward_list = []
    print("Start learning")
    while True:
        time_in = time.time()
        step += 1
        state = get_state()  # get new state
        all_reward = path_metrics_to_reward()
        drl_paths = {}
        reward_all = 0
        for i in range(1,SIZE):
            drl_paths.setdefault(str(i), {})
            for j in range(1,SIZE):
                if i != j:
                    reward = all_reward[str(i)][str(j)][int(action_memory[i][j])]
                    reward_all += reward
                    if step != 1:
                        brain[i][j].append_sample(state_memory,tf.convert_to_tensor(action_memory[i][j], dtype=tf.int32),state,reward)
                    action,q_value = brain[i][j].get_action([state],epsilon)
                    action_memory[i][j] = action
                    drl_paths[str(i)][str(j)] = [all_path_list[i][j][action]]
                    if len(brain[i][j].memory) > brain[i][j].batch_size:
                        
                        brain[i][j].update()
                        if step % 30 == 0:
                            print("network update")
                            brain[i][j].update_target()
                        if step % 3000 == 0:
                            brain[i][j].save_model(i,j)
        if step == 3000:
            return
        # write route path
        with open('./drl_paths.json','w') as json_file:
            json.dump(drl_paths, json_file, indent=2)

        time_end = time.time()
        print("calculate time:  ",time_end - time_in)
        state_memory = state
        reward_list.append(int(reward_all))
        path = 'output.txt'
        f = open(path, 'w')
        f.writelines(str(reward_list))
        f.close()
        print("------------------------------------------ step %d ------------------------------------------" % step)
        print("------------------------------------------  epsilon  %f ------------------------------------------   " % epsilon)
        if time_end - time_in < 10 :
            time.sleep(10 - (time_end - time_in)) # wait for monitor period
        if epsilon > epsilon_final:
            epsilon = epsilon*0.99


def DRL_thread_rank():
    print("enter thread")
    column, row = SIZE,SIZE
    brain = [[0]*row for _ in range(column)]
    for i in range(1,SIZE):
        for j in range(1,SIZE):
            if i!=j:
                brain[i][j] =  agent.Agent()

    all_path_list = state_to_action()

    step = 0
    epsilon_ini = 0.1
    epsilon_final = 0.01
    epsilon = 0.1
    action_memory = np.zeros((24,24))
    state_memory = np.zeros((24,24))
    reward_list = []
    print("Start learning")
    while True:
        time_in = time.time()
        step += 1
        state = get_state()  # get new state
        all_reward = path_metrics_to_reward_rank()
        drl_paths = {}
        reward_all = 0
        for i in range(1,SIZE):
            drl_paths.setdefault(str(i), {})
            for j in range(1,SIZE):
                if i != j:
                    reward = all_reward[str(i)][str(j)][int(action_memory[i][j])]
                    reward_all += reward
                    if step != 1:
                        brain[i][j].append_sample(state_memory,tf.convert_to_tensor(action_memory[i][j], dtype=tf.int32),state,reward)
                    action,q_value = brain[i][j].get_action([state],epsilon)
                    action_memory[i][j] = action
                    drl_paths[str(i)][str(j)] = [all_path_list[i][j][action]]

                    if len(brain[i][j].memory) > brain[i][j].batch_size:
                        brain[i][j].update()
                        
                        if step % 30 == 0:
                            print("network update")
                            brain[i][j].update_target()
                        if step % 3000 == 0:
                            brain[i][j].save_model(i,j)

        if step == 3000:
            return

        # write route path
        with open('./drl_paths.json','w') as json_file:
            json.dump(drl_paths, json_file, indent=2)

        time_end = time.time()
        print("calculate time:  ",time_end - time_in)
        state_memory = state
        reward_list.append(int(reward_all))
        path = 'output.txt'
        f = open(path, 'w')
        f.writelines(str(reward_list))
        f.close()
        print("------------------------------------------ step %d ------------------------------------------" % step)
        print("------------------------------------------  epsilon  %f ------------------------------------------   " % epsilon)
        if time_end - time_in < setting.MONITOR_PERIOD :
            time.sleep(setting.MONITOR_PERIOD - (time_end - time_in)) # wait for monitor period
        if epsilon > epsilon_final:
            epsilon -= (epsilon_ini - epsilon_final)/2000


def DRL_eval():
    column, row = SIZE,SIZE
    brain = [[0]*row for _ in range(column)]
    print("load model...")
    for i in range(1,SIZE):
        for j in range(1,SIZE):
            if i!=j:
                brain[i][j] =  agent.Agent()
                brain[i][j].load_model(i,j)
                print("load model....   ",i,"\t",j)
    all_path_list = state_to_action()
    print("Start eval")

    while True:
        time_in = time.time()
        state = get_state()  # get new state
        drl_paths = {}
        for i in range(1,SIZE):
            drl_paths.setdefault(str(i), {})
            for j in range(1,SIZE):
                if i != j:
                    action,q_value = brain[i][j].get_action([state],0)
                    drl_paths[str(i)][str(j)] = [all_path_list[i][j][action]]

        # write route path
        with open('./drl_paths.json','w') as json_file:
            json.dump(drl_paths, json_file, indent=2)
        time_end = time.time()
        print("eval time:  ",time_end - time_in)
        if time_end - time_in < setting.MONITOR_PERIOD :
            time.sleep(setting.MONITOR_PERIOD - (time_end - time_in)) # wait for monitor period



def path_metrics_to_reward():
        
    # read path metrices file
    file = './paths_metrics.json'
    rewards_dic = {}
    metrics = ['bwd_paths','delay_paths','loss_paths']
    try:
        with open(file,'r') as json_file:
            paths_metrics_dict = json.load(json_file)
            paths_metrics_dict = ast.literal_eval(json.dumps(paths_metrics_dict))
    except:
        time.sleep(0.35) # wait until file is ok
        with open(file,'r') as json_file:
            paths_metrics_dict = json.load(json_file)
            paths_metrics_dict = ast.literal_eval(json.dumps(paths_metrics_dict))


    for i in paths_metrics_dict:
        rewards_dic.setdefault(i,{})
        for j in paths_metrics_dict[i]:
            rewards_dic.setdefault(j,{})
            for m in metrics:
                if m == metrics[0]:
                    bwd_cost = []
                    for val in paths_metrics_dict[str(i)][str(j)][m][0]:
                        bwd_cost.append(round(val, 15))
                    paths_metrics_dict[str(i)][str(j)][m][0] = bwd_cost
                    met_norm = [normalize(met_val, 0, 100, min(paths_metrics_dict[str(i)][str(j)][m][0]), max(paths_metrics_dict[str(i)][str(j)][m][0])) for met_val in paths_metrics_dict[str(i)][str(j)][m][0]]
                else:    
                    met_norm = [normalize(met_val, 100, 0, min(paths_metrics_dict[str(i)][str(j)][m][0]), max(paths_metrics_dict[str(i)][str(j)][m][0])) for met_val in paths_metrics_dict[str(i)][str(j)][m][0]]
                paths_metrics_dict[str(i)][str(j)][m].append(met_norm)
    
    for i in paths_metrics_dict:
        for j in paths_metrics_dict[i]:
            rewards_actions = []              
            for act in range(20):
                rewards_actions.append(reward(i,j,paths_metrics_dict,act,metrics))
                rewards_dic[i][j] = rewards_actions
    return rewards_dic


def path_metrics_to_reward_rank():
        
    # read path metrices file
    file = './paths_metrics.json'
    rewards_dic = {}
    metrics = ['bwd_paths','delay_paths','loss_paths']
    try:
        with open(file,'r') as json_file:
            paths_metrics_dict = json.load(json_file)
            paths_metrics_dict = ast.literal_eval(json.dumps(paths_metrics_dict))
    except:
        time.sleep(0.35) # wait until file is ok
        with open(file,'r') as json_file:
            paths_metrics_dict = json.load(json_file)
            paths_metrics_dict = ast.literal_eval(json.dumps(paths_metrics_dict))


    for i in paths_metrics_dict:
        rewards_dic.setdefault(i,{})
        for j in paths_metrics_dict[i]:
            rewards_dic.setdefault(j,{})
            for m in metrics:
                if m == metrics[0]:
                    bwd_cost = [] 
                    for val in paths_metrics_dict[str(i)][str(j)][m][0]:
                        bwd_cost.append(round(val, 15))
                    paths_metrics_dict[str(i)][str(j)][m][0] = bwd_cost
                    met_norm = [normalize(met_val, 0, 100, min(paths_metrics_dict[str(i)][str(j)][m][0]), max(paths_metrics_dict[str(i)][str(j)][m][0])) for met_val in paths_metrics_dict[str(i)][str(j)][m][0]]
                else:    
                    met_norm = [normalize(met_val, 100, 0, min(paths_metrics_dict[str(i)][str(j)][m][0]), max(paths_metrics_dict[str(i)][str(j)][m][0])) for met_val in paths_metrics_dict[str(i)][str(j)][m][0]]
                paths_metrics_dict[str(i)][str(j)][m].append(met_norm)
    

    for i in paths_metrics_dict:
        for j in paths_metrics_dict[i]:
            rewards_actions = []              
            for act in range(20):
                rewards_actions.append(reward_rank(i,j,paths_metrics_dict,act,metrics))
            rewards_dic[i][j] = rewards_actions


    return rewards_dic          

def normalize(value, minD, maxD, min_val, max_val):
    if max_val == min_val:
        value_n = (maxD + minD) / 2 
    else:
        value_n = (maxD - minD) * (value - min_val) / (max_val - min_val) + minD
    return round(value_n,15)
                    

def get_state(): # get the current network state
    state = np.zeros((37,3))

    try:
        file = "./net_info.csv"
        data = pd.read_csv(file)
        for i in range(37):
            state[i][0] = data["bwd"][i]
            state[i][1] = data["delay"][i]
            state[i][2] = data["pkloss"][i]
        state_0 = np.array([100000,100000,100000,100000,100000,100000,100000,25000,25000,100000,
25000,1550,100000,100000,25000,25000,1550,1550,100000,25000,
100000,25000,25000,100000,25000,100000,100000,100000,100000,1550,
100000,25000,25000,100000,25000,25000,25000])
        state = np.insert(state, 0, values=state_0, axis=1)
        return state
    except:
        time.sleep(0.35)
        file = "./net_info.csv"
        data = pd.read_csv(file)
        for i in range(37):
            state[i][0] = data["bwd"][i]
            state[i][1] = data["delay"][i]
            state[i][2] = data["pkloss"][i]
        state_0 = np.array([100000,100000,100000,100000,100000,100000,100000,25000,25000,100000,
25000,1550,100000,100000,25000,25000,1550,1550,100000,25000,
100000,25000,25000,100000,25000,100000,100000,100000,100000,1550,
100000,25000,25000,100000,25000,25000,25000])
        state = np.insert(state, 0, values=state_0, axis=1)
        return state

def reward_rank(src, dst, paths_metrics_dict, act, metrics):

    beta1=1
    beta2=1
    beta3=1

    save_bwd = 0
    save_delay = 0
    save_loss = 0

    bwd_sort = sorted(paths_metrics_dict[str(src)][str(dst)][metrics[0]][1])
    for rank in range(20):
        if paths_metrics_dict[str(src)][str(dst)][metrics[0]][1][act] == bwd_sort[rank]:
            save_bwd = rank

    delay_sort = sorted(paths_metrics_dict[str(src)][str(dst)][metrics[1]][1])

    for rank in range(20):
        if paths_metrics_dict[str(src)][str(dst)][metrics[1]][1][act] == delay_sort[rank]:
            save_delay = rank

    loss_sort = sorted(paths_metrics_dict[str(src)][str(dst)][metrics[2]][1])

    for rank in range(20):
        if paths_metrics_dict[str(src)][str(dst)][metrics[2]][1][act] == loss_sort[rank]:
            save_loss = rank

    reward =beta1*save_bwd + beta2*save_delay + beta3*save_loss
    return reward

def reward(src, dst, paths_metrics_dict, act, metrics):
    '''
    paths_metrics_dict ={src:{dst:{metric1:[[orig value list],[normalized value list]]},metric2...}}
    '''
    beta1=1
    beta2=1
    beta3=1
    reward = beta1*paths_metrics_dict[str(src)][str(dst)][metrics[0]][1][act] + beta2*paths_metrics_dict[str(src)][str(dst)][metrics[1]][1][act] + beta3*paths_metrics_dict[str(src)][str(dst)][metrics[2]][1][act]
    return round(reward,15)

def state_to_action(): # 20 paths according src,dst
    file = './Routing/k_paths.json'
    paths = []
    with open(file,'r') as json_file:
        paths = json.load(json_file)
    column, row = SIZE,SIZE
    paths_20 = [[0]*row for _ in range(column)]
    for i in range(1,SIZE):
        for j in range(1,SIZE):
            if i != j:
                paths_20[i][j] = paths[str(i)][str(j)]
    return paths_20
if __name__ == "__main__":
    print("1 : learning phase Reward classic\n2 : learning phase Reward rank")
    i = input()
    if i == str(1):
        DRL_thread()
    elif i == str(2):
        DRL_thread_rank()
    else:
        DRL_eval()
