# Intelligent-Routing
## Traffic generator

進入geant_traffic資料夾  
執行generate_tms.py後會產生.pkl檔案  
再執行iperf3_scripts.py會產生TM-00、TM-01....資料夾  
將這些資料夾放入23nodos供後面產生流量使用


## Mininet

執行geant_mininet.py，controller IP需要自己設定  
開啟後會有4個選擇 CLI/CON/GEN/QUIT
* CLI
進入mininet介面
* CON
每個host先做一次ping操作，在拓樸建立完成時要先執行一次讓controller拿到相關資訊
* GEN
使用TM-XX(00、01.....)資料產生網路流量
* QUIT
離開mininet

## Controller

### ryu controller install

使用python 3.7

先去[ryu controller github](https://github.com/faucetsdn/ryu) 下載code
載完後進入ryu資料夾，執行pip3 install .

在此ryu版本裡會缺少我們需要的一些function  [ryu controller fix code](https://github.com/muzixing/ryu/blob/master/ryu/topology/switches.py)  
所以我們需要自己對此做出修改

1. 進入ryu/ryu/topology/switches.py
2. class PortData 裡的init多加一個self.delay = 0  
![](https://i.imgur.com/E9RPmRz.png)
3. 在lldp_packet_in_handler開頭先新增一行code : recv_timestamp = time.time()
4. 將fix版本code的714行後的get the lldp delay code 複製
![image](https://user-images.githubusercontent.com/69691891/145552471-a11fbc18-a494-4e34-982c-6e88a861a27a.png)
5. 將剛剛複製好的code貼到791行
6. 上述動作執行完成後，回到ryu資料夾並執行python3 setup.py install

### ryu controller usage

建議將mininet主機以及controller主機分開

使用 ryu-manager --observe-link simple_monitor.py 執行controller
執行myDRL使用RL agent進行轉發路徑的學習




