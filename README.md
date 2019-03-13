# TAutoNet

## Features
- Network Config: 可基于配置启动 okchain 测试网络
- Batch Apply Ops: 可定向对节点分组(如ds/lookup/miner)，或节点（如 192.168.168.22:26000）,或具体角色（如：DSNode, DSLead, IdleNd, LKNode, ShLead, ShNode） 执行批量操作
- Batch Check Result: 可定向对节点分组，或节点执行验证操作
- Test Case: 可为迭代开发提供基础的功能测试案例集合

## How to Use it
TAutoNet可根据输入配置(如 [sample.input](./tcases/sample.input) )快速构造分布式环境下的集成测试网络，在测试网络启动后，客户端TClient 网络中节点执行一系列操作后, TClient根据预期配置（如 [sample.output](./tcases/sample.expect) )检查网络节点中的状态（如块高、网络连接数等）是否与预期一致，最后每项检查结果被保存在样例配置文件的同级目录下。

### 1. 系统环境配置

- virtualenv, 准备 python 运行时环境
```
cd $TAUTONET_SOURCE_DIR;
pip install virtualenv
virtualenv -p python2.7 ./vevn27
source ./vevn27/bin/activate
```
- 需要为待运行测试网络的机器上设置免密登录,根据提示输入密码。DEST_HOST_IP 为 待运行 Peer 的主机IP
```
ssh-copy-id root@$DEST_HOST_IP
```

- 安装 TAutoNet
```
cd $TAUTONET_SOURCE_DIR;
source ./vevn27/bin/activate
bash -x ./install.sh
```

### 2.配置文件说明

*.input, *.output 测试案例的配置文件格式皆为json. 小工具：
[jsonformatter](https://jsonformatter-online.com/)

1. *.input
- sample.input 示例

```
{
  <!--、 1. 初始化 OKChain 网络配置-->
  "network_desc" : {
    "init_ds_leader_addr" : "192.168.168.22:25000",
    "192.168.168.22" : {
      "ds"     : {"grpc_port_start" : 25000, "grpc_port_end" : 25003},
      "miner"  : {"grpc_port_start" : 25010, "grpc_port_end" : 25019},
      "lookup" : {"grpc_port_start" : 25030, "grpc_port_end" : 25031}
    }
  },

  <!--2. OKChain网络启动之后按顺序执行以下 Action-->
  "setup_actions" : [
    [0, 1, "*",      "cleanup_data_dir",   {}],
    [3, 1, "*",      "start_okc_peer",     {}],
    [0, 1, "ds",     "set_primary",        {}],
    [0, 1, "miner",  "start_pow",          {}]
  ],

   <!--3. setup_actions 执行完后等待的秒数-->
   "wait_after_setup" : 60,

   <!--4. 定向对节点调用按顺序执行以下 Action-->
   "apply_actions" : [
    [0, 0, "192.168.168.22:25100", "send_transactions", {"hexFrom" : "9B175D69A0A3236A1E6992D03FA0BE0891D8D023", "hexTo" : "D8104E3E6DE811DD0CC07D32CCCE2F4F4B38403A", "amount" : 100, "count" : 1}]
  ],

  <!--5. apply_actions 执行完成等待的秒数，等待结束后，将基于 sample.expect 验证节点状态是否与预期一致-->
  "wait_after_apply" : 60,

   <!--6. 案例执行结束前执行的清理操作（未实现）-->
  、"teardown_actions" : [
  ]
}
```

- action 说明
 * 每个 Action 通过一个包含五个元素的列表来描述


| index    |      desc     | value type  |
|----------|:-------------:|------:|
| 0 |  action 执行后等待的秒数 | >=0 |
| 1 |    action 重复的次数   |  >=0  |
| 2 | apply action 的节点 |    '*' 表示所有节点; ds/miner/lookup表示特定类型的节点；DSNode, DSLead, IdleNd, LKNode, ShLead, ShNode 为更细粒度角色的节点； $ip:$grpc_port 表示特定节点|
| 3 | action name |   支持的操作：cleanup_data_dir，start_okc_peer，set_primary，start_pow，以及所有的 grpc. 具体操作列表请参考 [tbase::BaseNode](./autonet/tbase.py) |
| 4 | action kw args |   action 执行时传入的参数 |

```
    <!--对【所有】节点，执行 start_okc_peer(), 重复次数为1，执行完毕后等待 3 s-->
    [3, 1, "*",      "start_okc_peer",     {}],
```


2. *.expect // sample.expect

每个 expect 通过一个包含三个元素的列表来描述

| index    |      desc     | value type  |
|----------|:-------------:|------:|
| 0 | apply action 的节点 |    '*' 表示所有节点; ds/miner/lookup表示特定类型的节点； DSNode, DSLead, IdleNd, LKNode, ShLead, ShNode 为更细粒度角色的节点；$ip:$grpc_port 表示特定节点|
| 1 | action name |   支持的操作操作列表请参考 [tbase::BaseNode](./autonet/tbase.py) |
| 2 | 检查结果有效性的逻辑表达式 |  r 为 action 执行的返回值，这个表达示执行结果为 bool 值，即 true 或 false |


```
[
     <!--对【miner】节点，获取网络信息r， 其 RemotePeerList 的长度的范围为 >= 5 且 <= 15-->
    、["miner",  "GetNetworkInfo", "len(r.RemotePeerList) >= 6 and len(r.RemotePeerList) <= 15 "],
]
```

3. ./tcases/hostnames.json
测试案例中 *.expect, *.input 中 DomainName 与 IP 的映射表。如果需要在本地运行测试案例，需要修改 default_user为 ssh 登陆用户。
```
{
    "okchain0"      : "192.168.13.123",
    "okchain1"      : "192.168.13.122",
    "okchain0.com"  : "192.168.13.123",
    "okchain1.com"  : "192.168.13.122",
    "default_user"  : "root"
}
```

### 3. 运行案例与输出
1. 运行案例
```
方法一：
运行 autonet/utest/tcase.py 下的单元测试
python -m unittest an_utest.tcase.MyTestCase.test_AutoCase

方法二：
tclient.py run sample
```

2. 清理环境(非正常结束运行案例)
```
tclient.py force_clean sample
```

3.  *.output // sample.output 示例

- tclient.py 的运行时日志位于  /opt/tautonet/v1/logs/global.log
- 输出测试结果位于 /opt/tautonet/tcases/output/ 下
```
{
    "GetNetworkInfo @@ miner @@ [len(r.RemotePeerList) >= 6 and len(r.RemotePeerList) <= 15 ]": {
        "details": {
            "192.168.168.22:25010": "PASS",
            "192.168.168.22:25011": "PASS",
            "192.168.168.22:25012": "PASS",
            "192.168.168.22:25013": "PASS",
            "192.168.168.22:25014": "PASS",
            "192.168.168.22:25015": "PASS",
            "192.168.168.22:25016": "PASS",
            "192.168.168.22:25017": "PASS",
            "192.168.168.22:25018": "PASS",
            "192.168.168.22:25019": "PASS"
        },
        "group_chk_result": "PASS"
    },
}
```