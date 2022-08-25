在這裡有一個23nodos資料夾  
裡面需要放入一些產生流量腳本  
產生流量腳本的流程可以進入traffic generator資料夾看

當上述工作都做完後  
執行geant.py  
因為mininet需要root權限，因此需要sudo  
sudo python geant.py

成功執行後，會有5個選項可以選擇

* CLI   
 進入mininet command line介面
* TRA   
 產生training所需要的流量
* TEST   
 使用TM-XX(00、01.....)資料產生網路流量進行效能測試
* KILL   
 結束所有iperf3的process
* QUIT   
 結束mininet
