# -*- coding: utf-8 -*-
# @Time    : 2018/11/8 下午5:14
# @Author  : lingting.fu
# @Email   : lingting.fu@okcoin.com
# @File    : tnet.py
# @Software: TAutoNet

from autonet.tbase import BaseNode, OKCConst
from autonet.utils import LOG, log_traceback_str, log_exception, log_input_output
from threading import Thread
import time
import json
import os

class TAutoNet(object):

    VALID_ROLES = [
        "ds",
        "miner",
        "lookup",
        "idle",
        "DSNode",
        "DSLead",
        "IdleNd",
        "LKNode",
        "ShLead",
        "ShNode",
    ]

    HOST_MAP = {}

    def __init__(self, network_desc={}):
        self._network_desc = network_desc
        self.network_refresher = None
        self._ds_node_addrs = None
        self._lookup_node_addrs = None
        self._init_network_roles_map = {}
        self._prev_network_roles_map = {}
        self._crrt_network_roles_map = {}
        self._nodename_2_grpcaddr = {}
        self._grpcaddr_2_nodename = {}
        self._grpcaddr_2_okcnode = {}
        self._removed_okcnodes = {}
        self.load_okc_network()

    def get_all_nodes(self):
        return self._grpcaddr_2_okcnode.values()

    def get_node_by_grpc_addr(self, addr):
        alias_addr = self.get_alias_addr(addr)
        return self._grpcaddr_2_okcnode.get(alias_addr, alias_addr)

    def get_node_by_nodename(self, nodename):
        addr = self._nodename_2_grpcaddr.get(nodename)
        if addr != None:
            return self._grpcaddr_2_okcnode.get(addr)

    def add_new_node(self, host="0.0.0.0", grpc_port=20060, role="miner"):

        host_ip = self.get_alias_hostip(host)

        info = {
            "host": host_ip,
            "init_peer_role": role,
            "jrpc_port": grpc_port + 1000,
            "grpc_port": grpc_port,
            "init_ds_leader_addr": self._network_desc["init_ds_leader_addr"],
            "startup_ds_addresses" : self._ds_node_addrs,
            "startup_lookup_addresses" : self._lookup_node_addrs,
            "sharding_size" : self._network_desc.get("sharding_size", 5),
            "enable_pprof" : int(self._network_desc.get("enable_pprof", False))
        }
        n = BaseNode(**info)
        self._grpcaddr_2_nodename[n.grpc_addr] = n.node_name
        self._nodename_2_grpcaddr[n.node_name] = n.grpc_addr
        self._grpcaddr_2_okcnode[n.grpc_addr] = n
        n.get_ssh_client().start_okc_peer()


    @classmethod
    def get_alias_hostip(cls, hostname):

        if len(cls.HOST_MAP) == 0:
            from tcase import AutoCase
            if len(AutoCase.HOST_MAP.keys()) > 0:
                cls.HOST_MAP = AutoCase.HOST_MAP
            else:
                fpath = "/opt/tautonet/tcases/hostnames.json"
                with open(fpath, "r") as f:
                    txt = f.read()
                    cls.HOST_MAP = json.loads(txt)

        return cls.HOST_MAP.get(hostname, hostname)

    @classmethod
    def get_alias_addr(cls, addr):
        host, port = addr.split(":")
        ip = cls.get_alias_hostip(host)
        alias_addr = "%s:%s" % (ip, port)
        return alias_addr


    def load_okc_network(self):
        all_node_info = []
        init_ds_leader_addr = self._network_desc.get("init_ds_leader_addr")
        self.refresh_interval = self._network_desc.get("refresh_interval")
        self.network_refresher = TAutoNet.RefreshThread(self, self.refresh_interval)

        for host, info in self._network_desc.items():
            if not (host.startswith("192") or host.startswith("okchain")):
                continue

            startup_role_orders = ["lookup", "ds", "miner", "idle"]
            for role in startup_role_orders:
                port_info = info.get(role)
                if port_info == None:
                    continue

                start_port = port_info.get("grpc_port_start", -1)
                end_port = port_info.get("grpc_port_end", -1)
                if start_port == -1 or end_port == -1 or end_port < start_port:
                    continue

                x = start_port
                host_ip = self.get_alias_hostip(host)
                while x <= end_port:
                    peer_info = {
                        "host"                  : host_ip,
                        "init_peer_role"        : role,
                        "jrpc_port"             : x + 1000,
                        "grpc_port"             : x,
                        "init_ds_leader_addr"   : init_ds_leader_addr,
                        "sharding_size"         : self._network_desc.get("sharding_size", 5),
                        "enable_pprof"          : int(self._network_desc.get("enable_pprof", 0))
                    }
                    all_node_info.append(peer_info)
                    x += 1

        ds_node_addrs = map(lambda x: "%s:%d" % (x["host"], x["grpc_port"]), filter(lambda x: x["init_peer_role"] == "ds", all_node_info))
        lookup_node_addrs = map(lambda x: "%s:%d" % (x["host"], x["grpc_port"]), filter(lambda x: x["init_peer_role"] == "lookup", all_node_info))
        miner_node_addrs = map(lambda x: "%s:%d" % (x["host"], x["grpc_port"]), filter(lambda x: x["init_peer_role"] == "miner", all_node_info))
        self._ds_node_addrs = ds_node_addrs
        self._lookup_node_addrs = lookup_node_addrs

        for n in all_node_info:
            n["startup_ds_addresses"] = ds_node_addrs
            n["startup_lookup_addresses"] = lookup_node_addrs
            node = BaseNode(**n)
            self._grpcaddr_2_nodename[node.grpc_addr] = node.node_name
            self._grpcaddr_2_okcnode[node.grpc_addr] = node
            self._nodename_2_grpcaddr[node.node_name] = node.grpc_addr

        self._init_network_roles_map = {
            "ds"        : ds_node_addrs,
            "lookup"    : lookup_node_addrs,
            "miner"     : miner_node_addrs,
        }

        self._crrt_network_roles_map = self._init_network_roles_map
        self._prev_network_roles_map = self._crrt_network_roles_map

    def get_init_network_roles_map(self):
        return self._init_network_roles_map

    def startup_nodes(self):
        for node in self._grpcaddr_2_okcnode.values():
            node.get_ssh_client().start_okc_peer()

    def shutdown_nodes(self):
        for node in self._grpcaddr_2_okcnode.values():
            node.get_ssh_client().kill_okc_peer()

    @log_exception
    def remove_killed_node(self, node):
        self._removed_okcnodes[node.grpc_addr] = node
        n = self._grpcaddr_2_okcnode.pop(node.grpc_addr)
        n.get_ssh_client().close()
        n.get_grpc_client().close()

    def cleanup_data(self):
        for node in self._grpcaddr_2_okcnode.values():
            node.get_ssh_client().cleanup_data_dir()

    def locate_nodes(self, role_or_addr):
        '''
        locate nodes by role or addr in the test network.
        :param role_or_addr:  it could be one of ['ds', 'miner', 'lookup', 'DSNode', 'DSLead', 'IdleNd', 'LKNode', 'ShLead', 'ShNode']
                              or an grpc_address e.g.) 0.0.0.0:25000
                              or miner.0, LKNode.0

        :return: nodes' list
        '''
        nodes = []
        result = role_or_addr.split("@")
        index = None
        role_or_addr = result[0]
        if len(result) == 2:
            index = int(result[1])

        if role_or_addr in self.VALID_ROLES:
            grpc_addresses = self._crrt_network_roles_map.get(role_or_addr)
            if grpc_addresses == None or len(grpc_addresses) == 0:
                return nodes

            for g_a in grpc_addresses:
                n = self._grpcaddr_2_okcnode.get(g_a)
                if n == None:
                    LOG.error("%s not found, %s" % (g_a, self._crrt_network_roles_map))
                else:
                    nodes.append(n)
        else:
            n = self.get_node_by_grpc_addr(role_or_addr)
            if n == None:
                LOG.error("%s not found, %s" % (role_or_addr, self._crrt_network_roles_map))
            else:
                nodes.append(n)

        if len(nodes) > 0 and index != None:
            return [nodes[index]]

        return nodes

    @log_exception
    def _format_node_status(self, node, node_status, node_name="default"):
        if node == None or node_status == None:
            return "%s Not Reachable, it maybe die." % node_name

        m = {
            "addr"      : node.grpc_addr,
            "role"      : OKCConst.BrifeRoleTypeMap.get(node_status.crrRoleName, node_status.crrRoleName),
            "fsmState"  : OKCConst.BrifeRoleTypeMap.get(node_status.crrFSMStatus, node_status.crrFSMStatus),
            "peerCnt"   : node_status.crrGspPeersCnt,
            "dsHeight"  : node_status.crrDSHeight,
            "txHeight"  : node_status.crrTxHeight,
            "shdID"     : node_status.shardId,
        }
        return "%(addr)s ShdID-%(shdID)s PeerCnt-%(peerCnt)d:DsNO-%(dsHeight)d:TxNO-%(txHeight)d %(role)s@%(fsmState)s" % m

    def refresh_network(self):

        _crrt_network_roles_map = {}
        for x in OKCConst.GroupType_2_RoleType.keys():
            _crrt_network_roles_map[x] = []
        for x in OKCConst.BrifeRoleTypeMap.values():
            _crrt_network_roles_map[x] = []

        peer_status = {}
        msgs = ["\n"]
        for adr, node in self._grpcaddr_2_okcnode.items():
            status = node.GetPeerStatus()
            peer_status[adr] = status
            if status != None:
                try:
                    grp_type = OKCConst.RoleType_2_GroupType[status.crrRoleName]
                    _crrt_network_roles_map[grp_type].append(node.grpc_addr)

                    role_in_short = OKCConst.BrifeRoleTypeMap[status.crrRoleName]
                    _crrt_network_roles_map[role_in_short].append(node.grpc_addr)

                except Exception as e:
                    log_traceback_str()

            msg = self._format_node_status(node, status, adr)
            msgs.append(msg)

        final_msg = "\n".join(sorted(msgs))
        LOG.info(final_msg)

        self._prev_network_roles_map = self._crrt_network_roles_map
        self._crrt_network_roles_map = _crrt_network_roles_map
        return peer_status

    def get_crrt_network_roles_map(self):
        return self._crrt_network_roles_map

    class RefreshThread(Thread):

        def __init__(self, net, refresh_interval):
            super(TAutoNet.RefreshThread, self).__init__(name="RefreshPeerThread")
            # self.setDaemon(True)
            self._net = net
            self._stop = False
            self._refresh_interval = refresh_interval

        def run(self):
            while not self._stop:
                time.sleep(self._refresh_interval)
                if not self._stop:
                    crr_peer_statuses = self._net.refresh_network()
                    die_peer_count = len(filter(lambda x: x == None, crr_peer_statuses.values()))
                    LOG.info("Network Group Map: %s" % self._net.get_crrt_network_roles_map())
                    if die_peer_count == len(crr_peer_statuses):
                        break
                else:
                    break

        def stop(self):
            self._stop = True


    @log_exception
    def apply_op(self, op_name, **op_kwargs):
        op = getattr(self, op_name)
        return op(**op_kwargs)

    def force_clean_env(self):
        if self.network_refresher != None:
            self.network_refresher.stop()

        n = self._grpcaddr_2_okcnode.values()[0]
        n.get_ssh_client().force_clean_env()