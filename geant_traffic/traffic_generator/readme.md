## Traffic Generator

# Download

在GEANT拓樸我們使用真實網路數據流量  
前往https://totem.info.ucl.ac.be/dataset.html 下載dataset
檔案下載下來後將檔案解壓縮，會有traffic-matrices資料夾，裡面會有許多
時間段的traffic matrix


# How to use

有了traffic-matrices資料夾後再執行iperf3_geant.py  
就會成功產生TM-00,TM-01...資料夾
在iperf3_geant.py裡可以更改日期，產生出的流量會根據所更改的日期  
產生TM-00,TM-01...資料夾後，將這些資料夾丟進23nodos資料夾裡以供使用
