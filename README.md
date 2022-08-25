# Intelligent-Routing
## Mininet

前往 https://github.com/mininet/mininet  
git clone https://github.com/mininet/mininet  
進入mininet/util 執行 ./install.sh  
安裝完後可以執行 sudo mn 看看有沒有正確安裝


## Controller

### ryu controller install

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
6. 上述動作執行完成後，回到ryu資料夾並執行pip3 install .

### ryu controller usage

進入Myself資料夾
使用 ryu-manager --observe-link simple_monitor.py 執行controller  

### DRL learning

執行myDRL.py 
輸入1為使用DRL agent進行轉發路徑的學習  
輸入2為效能測試時使用




