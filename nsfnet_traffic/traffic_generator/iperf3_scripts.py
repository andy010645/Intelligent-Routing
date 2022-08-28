import sys
import re
import os
from sys import argv
import statistics
import pickle
import time

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

file = '14Nodes_tms_info_24.pkl'
mean_loads_list = []
total_load_list = []
with open(file, 'rb') as f:
    od_bin,tms = pickle.load(f)

# tms_14_hours = ['00','01','03','05','07','09','10','11','12','14','16','18','20','22'] #choosen hours
tms_24_hours = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
j = 0

for tm in tms:
    #FOR CREATING FOLDERS PER TRAFFIC MATRIX  
    nameTM = 'TM-'+ str(int(tms_24_hours[j]))
    print('------',nameTM)
    if not os.path.exists(nameTM):
        os.mkdir(nameTM)

    #--------------------FLOWS--------------------------
    # FOR CREATING FOLDERS PER NODE
    for i in range(len(tm[0])):
        nameNode = str(nameTM)+'/Clients'
        if not os.path.exists(nameNode):
                os.mkdir(nameNode)
                # print("Folder created:", nameNode )

    for i in range(len(tm[0])):
        nameNode = str(nameTM)+'/Servers'
        if not os.path.exists(nameNode):
                os.mkdir(nameNode)
                # print("Folder created:", nameNode )

    # Default parameters
    time_duration = 50000

    throughput = 0.0 #take it in kbps from TM

    # Obtain parameters from arguments
    error = False
    for arg in sys.argv[1:]:
        option = arg.split("=")
        if (option[0] == int("--time")):
            time_duration = option[1]
        # elif (option[0] == "--ip_dest"):
        #     ip_dest = option[1]
        # elif (option[0] == "--port"):
        #     port = int(option[1])
        else:
            print ("Option %s is not valid" % option[0])
            error = True

    #UDP with time = 10s
    #   -c: ip_destination
    #   -b: throughput in k,m or g (Kbps, Mbps or Gbps)
    #   -t: time in seconds

    #SERVER SIDE 
    # iperf3 -s

    #CLIENT SIDE with iperf3
    # iperf3 -c <ip_dest> -u -p <port> -b <throughput> -t <duration> -V -J 

    #As we do not consider throughput in the same node, when src=dest the thro = 0
    for src in range(len(tm[0])):
        for dst in range(len(tm[0])):
            if src == dst and tm[src][dst] != 0.0:
                tm[src][dst] = 0.0

    for src in range(len(tm[0])):
        src_ = src+1
        #SCRIPT WITH COMMANDS FOR GENERATE TRAFFIC
        if src_ > 9:
            fileClient = open(str(nameTM)+"/Clients/client_{0}.sh".format(str(src_)), 'w')
        else:
            fileClient = open(str(nameTM)+"/Clients/client_0{0}.sh".format(str(src_)), 'w')
        outputstring_a1 = ''' #!/bin/bash \necho Generating traffic...
        '''
        fileClient.write(outputstring_a1)
        n=0
        for dst in range(len(tm[0])):
            dst_ = dst+1
            throughput = float(tm[src][dst])
            # throughput_g = throughput / (100) #scale the throughput value to mininet link capacities
            temp1 = ''
            if throughput != 0.0:
                n = n+1
                temp1 = ''
                temp1 += '\n'
                temp1 += 'iperf3 -c '
                temp1 += '10.0.0.{0} '.format(str(dst_))
                if dst_ > 9:   
                    temp1 += '-p {0}0{1} '.format(str(src_),str(dst_))
                else:
                    temp1 += '-p {0}00{1} '.format(str(src_),str(dst_))
                temp1 += '-u -b '+str(format(throughput,'.3f'))+'k'
                temp1 += ' -w 256k -t '+str(time_duration)+" -i 0"
                # if src_ > 9: 
                #     temp1 += ' > 23nodos/clientOutputs/'+str(nameTM)+'/client_{0}/clientOutput_{1}_to_{2}.log'.format(str(src_),str(src_),str(dst_))
                # else:
                #     temp1 += ' > 23nodos/clientOutputs/'+str(nameTM)+'/client_0{0}/clientOutput_{1}_to_{2}.log'.format(str(src_),str(src_),str(dst_))
                # if n != dst_amounts[src]: #When it is the last command, it does not include &
                temp1 += ' &\n' # & at the end of the line it's for running the process in bkg
                temp1 += 'sleep 0.4'

            fileClient.write(temp1)
        fileClient.close()
    # print(na)
    for dst in range(len(tm[0])):
        dst_ = dst+1
        
        #SCRIPT FOR COMMANDS TO INITIALIZE SERVERS LISTENING
        if dst_ > 9:
            fileServer = open(str(nameTM)+"/Servers/server_{0}.sh".format(str(dst_)), 'w') 
        else:
            fileServer = open(str(nameTM)+"/Servers/server_0{0}.sh".format(str(dst_)), 'w') 
        outputstring_a2 = ''' #!/bin/bash \necho Initializing server listening...
        '''
        fileServer.write(outputstring_a2)
        # n=0
        for src in range(len(tm[0])):
            src_ = src+1
            temp2 = ''
            if tm[src][dst] != 0:
                # n = n+1
                temp2 = ''
                temp2 += '\n'
                temp2 += 'iperf3 -s '
                if dst_ > 9:   
                    temp2 += '-p {0}0{1} '.format(str(src_),str(dst_))
                else:
                    temp2 += '-p {0}00{1} '.format(str(src_),str(dst_))
                temp2 += '-1 -i 0'
                # if dst_ > 9:
                #     temp2 += ' -J --logfile serverOutputs/'+str(nameTM)+'/server_{0}/serverOutput_{1}_to_{2}.json'.format(str(dst_),str(src_),str(dst_))  
                # else:    
                #     temp2 += ' -J --logfile serverOutputs/'+str(nameTM)+'/server_0{0}/serverOutput_{1}_to_{2}.json'.format(str(dst_),str(src_),str(dst_))  
                # if n != dst_amounts[src]: #When it is the last command, it does not include &
                temp2 += ' &\n' # & at the end of the line it's for running the process in bkg
                temp2 += 'sleep 0.3'
            fileServer.write(temp2)
        fileServer.close() 

    list_loads = []
    
    for src in range(len(tm[0])):
        src_ = src+1
        for dst in range(len(tm[0])):
            dst_ = dst+1
            if tm[src][dst]/100 != 0.0: #/100 to scale to mininet and it is in kbps
                list_loads.append(tm[src][dst])

    total = sum(list_loads)
    mean = statistics.mean(list_loads)
    print(total)
    print(mean)
    total_load_list.append(total)
    mean_loads_list.append(mean)
    #print(total_load_list)

    # print('Total load of TM {0}: {1}'.format(name, mean))
    #print('Mean load of TM {0}: {1}'.format(nameTM, total))

    j += 1
#print('List of mean load for each TM:', mean_loads_list)
#print('List of total load for each TM:', total_load_list)

tms_14_hours = [0,1,3,5,7,9,10,11,12,14,16,18,20,22] #tm hours
plt.plot(tms_14_hours,total_load_list,marker = 'o', linestyle = '')
plt.title(str(len(tms[0]))+"Nodes topology loads (14)")
plt.xlabel('Tms')
plt.ylabel('Load (Mbps)')
plt.xticks(tms_14_hours)
plt.grid()
plt.savefig(str(len(tms[0]))+"Nodes_load_14.eps",bbox_inches = 'tight') 
plt.close()
