# Intelligent-Routing
Intelligent Routing via Deep Reinforcement Learning in Software Defined Network
Ubuntu 20.04
## Installation
### Mininet

```
git clone https://github.com/mininet/mininet 
```
成功下載下來後會有一個mininet資料夾
進入mininet/util
```
cd mininet/util
```
執行安裝
```
./install.sh  
```
安裝完後可以進入terminal確認有無正確安裝
```
sudo mn
```


### Controller

```
https://github.com/faucetsdn/ryu
```
成功下載下來後會有一個ryu資料夾
進入ryu/ryu/topology
```
cd ryu/ryu/topology
```
裡面會有一個檔案為 switches.py
我們需要對這個檔案做出一些修改
* class PortData
```python3 
class PortData(object):
    def __init__(self, is_down, lldp_data):
        super(PortData, self).__init__()
        self.is_down = is_down
        self.lldp_data = lldp_data
        self.timestamp = None
        self.sent = 0
```
在後面在增加一行code
```python3
class PortData(object):
    def __init__(self, is_down, lldp_data):
        super(PortData, self).__init__()
        self.is_down = is_down
        self.lldp_data = lldp_data
        self.timestamp = None
        self.sent = 0
        self.delay = 0
```

* lldp_packet_in_handler
```python3
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def lldp_packet_in_handler(self, ev):
    if not self.link_discovery:
        return

    msg = ev.msg
    try:
        src_dpid, src_port_no = LLDPPacket.lldp_parse(msg.data)
    except LLDPPacket.LLDPUnknownFormat:
        # This handler can receive all the packets which can be
        # not-LLDP packet. Ignore it silently
        return

    dst_dpid = msg.datapath.id
    if msg.datapath.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
        dst_port_no = msg.in_port
    elif msg.datapath.ofproto.OFP_VERSION >= ofproto_v1_2.OFP_VERSION:
        dst_port_no = msg.match['in_port']
    else:
        LOG.error('cannot accept LLDP. unsupported version. %x',
                  msg.datapath.ofproto.OFP_VERSION)

    src = self._get_port(src_dpid, src_port_no)
    if not src or src.dpid == dst_dpid:
        return
```
修改為
```python3
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def lldp_packet_in_handler(self, ev):
    recv_timestamp = time.time()
    if not self.link_discovery:
        return

    msg = ev.msg
    try:
        src_dpid, src_port_no = LLDPPacket.lldp_parse(msg.data)
    except LLDPPacket.LLDPUnknownFormat:
        # This handler can receive all the packets which can be
        # not-LLDP packet. Ignore it silently
        return

    dst_dpid = msg.datapath.id
    if msg.datapath.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
        dst_port_no = msg.in_port
    elif msg.datapath.ofproto.OFP_VERSION >= ofproto_v1_2.OFP_VERSION:
        dst_port_no = msg.match['in_port']
    else:
        LOG.error('cannot accept LLDP. unsupported version. %x',
                  msg.datapath.ofproto.OFP_VERSION)

    for port in self.ports.keys():
        if src_dpid == port.dpid and src_port_no == port.port_no:
            send_timestamp = self.ports[port].timestamp
            if send_timestamp:
                self.ports[port].delay = recv_timestamp - send_timestamp
    src = self._get_port(src_dpid, src_port_no)
    if not src or src.dpid == dst_dpid:
        return
```
執行完上述動作後，回到ryu資料夾進行安裝
```
python3 setup.py install
```
安裝完成後
```
pip3 unstall .
```
結束ryu controller的安裝
可以在terminal確認有無正確安裝
```
ryu-manager
```

## Intelligent-Routing implement steps

```
git clone https://github.com/andy010645/Intelligent-Routing
```
成功下載後會有一個Intelligent-Routing資料夾
進入Intelligent-Routing/geant_traffic
```
cd Intelligent-Routing/geant_traffic
```
在此資料夾會有一些前置作業，可以參考此資料夾裡的readme  
當前置作業完成後，使用 geant.py 建立mininet環境
```
sudo python3 geant.py
```
當mininet啟動完成後我們開始啟動ryu-controller
進入Intelligent-Routing/ours

```
cd Intelligent-Routing/ours
```
執行controller
```
ryu-manager --observe-link simple_monitor.py
```
當controller成功啟動後，就可以開始在mininet環境傳輸流量
當訓練流量開始後執行我們的agent
```
python3 myDRL.py 
```
輸入1讓DRL agent進行轉發路徑的學習  
當訓練完成後，可以輸入2進行效能測試模式





