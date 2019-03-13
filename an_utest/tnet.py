import unittest
import time
import json

from autonet.tnet import TAutoNet

class MyTestCase(unittest.TestCase):

    def test_smoke(self):
        net_desc = {
            "init_ds_leader_addr" : "okchain0:25000",
            "okchain0" : {
              "ds"     : {"grpc_port_start" : 25000, "grpc_port_end" : 25003},
              "miner"  : {"grpc_port_start" : 25010, "grpc_port_end" : 25016},
              "lookup" : {"grpc_port_start" : 25030, "grpc_port_end" : 25031}
            }
        }
        nw = TAutoNet(net_desc)
        nw.load_okc_network()

        m = nw.get_init_network_roles_map()
        all_node_count = sum(map(lambda x: len(x), m.values()))
        assert m != None and 13 == all_node_count, (all_node_count, m)

        node = nw.get_node_by_grpc_addr("okchain0:25000")
        assert node != None, node

        node2 = nw.get_node_by_nodename(node.node_name)
        assert node2 != None and node2.node_name == node.node_name, (node, node2)

        nw.startup_nodes()
        assert node.get_ssh_client().check_okc_peer_count(1) == True, node
        assert node2.get_ssh_client().check_okc_peer_count(1) == True, node2

        time.sleep(2)
        peer_status = nw.refresh_network()
        assert peer_status != None and len(peer_status) > 0, peer_status

        nw.shutdown_nodes()
        assert node.get_ssh_client().check_okc_peer_count(0) == True, node
        assert node2.get_ssh_client().check_okc_peer_count(0) == True, node2

        ds_nodes = nw.locate_nodes("ds")
        ds_leader_nodes = nw.locate_nodes("okchain0:25000")
        assert ds_nodes != None and len(ds_nodes) == 4, ds_nodes
        assert ds_leader_nodes != None and len(ds_leader_nodes) == 1, ds_leader_nodes

    def test_hostname(self):
        d = {
            "okchain0" : "192.168.13.123",
            "okchain1" : "192.168.13.122",
        }

        print(json.dumps(d, indent=4))

        ip = TAutoNet.get_alias_hostip("okchain0")
        assert ip != None, ip


if __name__ == '__main__':
    unittest.main()
