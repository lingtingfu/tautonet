# -*- coding: utf-8 -*-
# @Time    : 2018/11/8 下午5:12
# @Author  : lingting.fu
# @Email   : lingting.fu@okcoin.com
# @File    : tbase.py
# @Software: TAutoNet

from autonet import utils
from autonet.okproto import explorer_pb2_grpc, explorer_pb2, okchain_pb2, okchain_pb2_grpc, inner_pb2, inner_pb2_grpc
from autonet.okproto.explorer_pb2 import EmptyRequest

import grpc
import json
import paramiko
import time


class OKCConst(object):

    PEER_ROLE_MINER         = "miner"
    PEER_ROLE_DS            = "ds"
    PEER_ROLE_LOOKUP        = "lookup"
    PEER_ROLE_IDLE          = "idle"

    # Old. before 2018.12
    # RoleTypeDirService      = "DirService"
    # RoleTypeDirServiceLead  = "DirServiceLead"
    # RoleTypeIdleRole        = "IdleRole"
    # RoleTypeLookup          = "LookupRole"
    # RoleTypeShardingLead    = "ShardingLead"
    # RoleTypeShardingNode    = "ShardingNode"


    # New. After 2018.12
    RoleTypeDirServiceBK    = "DsBackup"
    RoleTypeDirServiceLead  = "DsLead"
    RoleTypeIdleRole        = "Idle"
    RoleTypeLookup          = "Lookup"
    RoleTypeShardingLead    = "ShardLead"
    RoleTypeShardingBackup  = "ShardBackup"

    BrifeRoleTypeMap = {
        RoleTypeDirServiceBK    : "DSNode",
        RoleTypeDirServiceLead  : "DSLead",
        RoleTypeIdleRole        : "IdleNd",
        RoleTypeLookup          : "LKNode",
        RoleTypeShardingLead    : "ShLead",
        RoleTypeShardingBackup  : "ShNode"
    }

    RoleType_2_GroupType = {
        RoleTypeDirServiceBK    : PEER_ROLE_DS,
        RoleTypeDirServiceLead  : PEER_ROLE_DS,
        RoleTypeIdleRole        : PEER_ROLE_IDLE,
        RoleTypeLookup          : PEER_ROLE_LOOKUP,
        RoleTypeShardingLead    : PEER_ROLE_MINER,
        RoleTypeShardingBackup  : PEER_ROLE_MINER
    }

    GroupType_2_RoleType = {
        PEER_ROLE_DS        : [RoleTypeDirServiceBK, RoleTypeDirServiceLead],
        PEER_ROLE_MINER     : [RoleTypeShardingBackup, RoleTypeShardingLead],
        PEER_ROLE_LOOKUP    : [RoleTypeLookup],
        PEER_ROLE_IDLE      : [RoleTypeIdleRole]
    }

    class EnumConsensusRole:
        # ConsensusIDLE = 0
        ConsensusDSLEADER = 0
        ConsensusDSBACKUP = 1
        ConsensusSHARDINGLEADER = 2
        ConsensusSHARDINGNODE = 3

    class EnumConsensusMode:
        # IDLE = 0
        DSBlockConsensus = 0
        MircoBlockConsensus = 1
        FinalBlockConsensus = 2
        ViewChangeBlockConsensus = 3


class RpcClient(object):

    @utils.log_exception
    def __init__(self, host, port):
        self.conn = grpc.insecure_channel("%s:%d" % (host, port), options=[("timeout", 5), ("deadline", 5)])
        self.explorer_client = explorer_pb2_grpc.BackendStub(channel=self.conn)
        self.okc_client = okchain_pb2_grpc.PeerStub(channel=self.conn)
        self.inner_client = inner_pb2_grpc.InnerStub(channel=self.conn)
        self.host = host
        self.port = port

    def __repr__(self):
        return "RPCClient(%s:%d)" % (self.host, self.port)

    @utils.log_exception
    def close(self):
        self.conn.close()

    @utils.log_exception
    def GetLatestDsBlock(self):
        latest_ds = self.explorer_client.GetLatestDsBlock(EmptyRequest())
        return latest_ds

    @utils.log_exception
    def GetLatestTxBlock(self):
        latest_tx = self.explorer_client.GetLatestTxBlock(EmptyRequest())
        return latest_tx

    @utils.log_exception
    def GetNetworkInfo(self):
        network_info_request = explorer_pb2.NetworkInfoRequest()
        return self.explorer_client.GetNetworkInfo(network_info_request)

    @utils.log_exception
    def GetAccount(self, hexAddr=None):
        b_addr = bytes(bytearray.fromhex(hexAddr.replace("0x", "")))
        ar = explorer_pb2.AccountRequest(address=b_addr)
        return self.explorer_client.GetAccount(ar)

    @utils.log_exception
    def GetTransaction(self, hexTrxHash):
        b_addr = bytes(bytearray.fromhex(hexTrxHash.replace("0x", "")))
        trx_req = explorer_pb2.TransactionRequest(addr=b_addr)
        return self.explorer_client.GetTransaction(trx_req)

    @utils.log_exception
    def GetTransactionsByAccount(self, hexAddr):
        b_addr = bytes(bytearray.fromhex(hexAddr.replace("0x", "")))
        req = explorer_pb2.GetTransactionsByAccountRequest(address=b_addr)
        return self.explorer_client.GetTransactionsByAccount(req)

    @utils.log_exception
    @utils.log_input_output
    def SendTransaction(self, hexFromAddr=None, hexToAddr=None, amount=None, nonce=-1):
        b_fromAddr = bytes(bytearray.fromhex(hexFromAddr).replace("0x", ""))
        b_toAddr = bytes(bytearray.fromhex(hexToAddr).replace("0x", ""))
        transaction = okchain_pb2.Transaction(nonce=nonce, senderPubKey=b_fromAddr, toAddr=b_toAddr, amount=amount)
        return self.explorer_client.SendTransaction(transaction)

    @utils.log_exception
    def GetPeerStatus(self):
        return self.inner_client.GetPeerStatus(EmptyRequest(), timeout=30)


class OKCSSHClient(object):

    def __init__(self, host, ssh_port, jrpc_port, grpc_port, startup_lookup_addresses, startup_ds_addresses, peer_mode,
                 node_name, init_ds_leader_addr,
                 default_user="root", sharding_size=5, enable_pprof=False):
        '''
        前置条件：需要为待登陆机器设置免密登录,根据提示输入密码。 ssh-copy-id root@$IP
        :param host:
        :param port:
        '''
        self.__user = default_user
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.connect(hostname=host, port=ssh_port, username=self.__user)
        self.host = host
        self.jrpc_port = jrpc_port
        self.grpc_port = grpc_port
        self.startup_lookup_addresses = startup_lookup_addresses
        self.startup_ds_addresses = startup_ds_addresses
        self.peer_mode = peer_mode
        self.node_name = node_name
        self.sharding_size = sharding_size
        self.init_ds_leader_addr = init_ds_leader_addr
        self.enable_pprof = enable_pprof
        self.__init_okc_env()

    def __repr__(self):
        return "OKCSSHClient %s" % self.node_name

    def __init_okc_env(self):
        env_shell, _ = self._gen_okchain_env(self.jrpc_port,
                                             self.grpc_port,
                                             self.startup_lookup_addresses,
                                             self.startup_ds_addresses,
                                             self.peer_mode,
                                             self.node_name,
                                             self.sharding_size)

        self.script_path = "/tmp/profile_%s" % self.node_name
        self.execute_cmd("echo \"%s\" > %s" % (env_shell, self.script_path))

    @utils.log_input_output
    def execute_cmd(self, cmd):
        ssh_stdin, ssh_stdout, ssh_stderr = self._ssh.exec_command(cmd)
        return ssh_stdout.read(), ssh_stderr.read()

    @utils.log_input_output
    @utils.log_exception
    def execute_okc_cmd(self, cmd):
        return self.execute_cmd("source %s; %s" % (self.script_path, cmd))

    def _gen_okchain_env(self, jrpc_port, grpc_port, startup_lookup_addresses, startup_ds_addresses, peer_mode,
                         node_name, sharding_size):
        env_dict = {
            "jrpc_port"                 : jrpc_port,
            "grpc_port"                 : grpc_port,
            "gossip_port"               : grpc_port,
            "debug_port"                : grpc_port + 10000,
            "startup_lookup_addresses"  : "|".join(startup_lookup_addresses),
            "startup_ds_addresses"      : "|".join(startup_ds_addresses),
            "peer_mode"                 : peer_mode,
            "node_name"                 : node_name,
            "okcli_name"                : node_name + "_okcli",
            "sharding_size"             : sharding_size,
            "enable_pprof"              : 0 if self.enable_pprof == False else 1
        }

        env_shell = '''
#! /bin/bash 
        
export GOPATH=\${HOME}/go
export OKCHAIN_TOP=\${GOPATH}/src/github.com/ok-chain/okchain
export BUILD_BIN=\${OKCHAIN_TOP}/build/bin
export PEER_CLIENT_BINARY=\${BUILD_BIN}/okchaind
export OKCLI_BINARY=\${BUILD_BIN}/okchaincli
export OKCHAIN_DEV_SCRIPT_TOP=\$OKCHAIN_TOP/dev
export OKCHAIN_DEV_DATA_TOP=\$OKCHAIN_TOP/dev/autonet_data

export OKCHAIN_ACCOUNT_KEYSTOREDIR=\${OKCHAIN_TOP}/dev/keystore
export OKCHAIN_PEER_JSONRPCADDRESS="0.0.0.0":%(jrpc_port)d
export OKCHAIN_PEER_GOSSIP_LISTENPORT=%(gossip_port)d
export OKCHAIN_PEER_GRPC_LISTENPORT=%(grpc_port)d
export OKCHAIN_PEER_MODE=%(peer_mode)s
export OKCHAIN_PEER_ENABLEPPROF=%(enable_pprof)s
export OKCHAIN_PEER_LISTENADDRESS="0.0.0.0":%(grpc_port)d
export OKCHAIN_PEER_DEBUG_LISTENADDRESS="0.0.0.0":%(debug_port)d
export OKCHAIN_PEER_DSLISTENADDRESS='%(startup_ds_addresses)s'
export OKCHAIN_PEER_LOOKUPNODEURL='%(startup_lookup_addresses)s'
# export OKCHAIN_PEER_GOSSIPPORTPREFIX=%(gossip_port)s
export OKCHAIN_PEER_DATADIR=\${OKCHAIN_DEV_DATA_TOP}/%(node_name)s    
export OKCHAIN_PEER_LOGPATH=\${OKCHAIN_PEER_DATADIR}/%(node_name)s.log
export OKCHAIN_PEER_ROLEID=%(node_name)s
export OKCHAIN_PEER_IPCENDPOINT=\${OKCHAIN_DEV_DATA_TOP}/%(node_name)s.ipc
export OKCHAIN_LEDGER_TXBLOCKCHAIN_GENESISCONF=\${OKCHAIN_TOP}/dev/genesis.json
export OKCHAIN_LEDGER_BASEDIR=\${OKCHAIN_PEER_DATADIR}/db/
export OKCHAIN_SHARDING_SIZE=%(sharding_size)d
export STDOUT_LOG_FILE=\${OKCHAIN_PEER_DATADIR}/stdout_%(node_name)s.log
export OKCHAIN_LOGGING_NODE=debug:ledger=debug:gossip=info:peer=debug:txpool=debug:blspbft=debug:role=debug

peer_keystore_dir=\${OKCHAIN_PEER_DATADIR}/keystore/
mkdir -p \$peer_keystore_dir
mkdir -p \$HOME/.okchain/keystore/
cp \$OKCHAIN_ACCOUNT_KEYSTOREDIR/* \$peer_keystore_dir 
cp \$OKCHAIN_ACCOUNT_KEYSTOREDIR/* \$HOME/.okchain/keystore/

mkdir -p \${OKCHAIN_PEER_DATADIR}
cd \${OKCHAIN_PEER_DATADIR}
ln -snf \${PEER_CLIENT_BINARY} %(node_name)s
ln -snf \${OKCLI_BINARY} %(okcli_name)s

''' % env_dict

        return env_shell, env_dict

    def _get_process_count_cmd(self, node_name):
        cmd = "ps aux | grep %s | grep -v grep | wc -l" % node_name
        return cmd

    def start_okc_peer(self):
        startup_cmd = "nohup ./%s node start >> ${STDOUT_LOG_FILE} 2>>${STDOUT_LOG_FILE} &" % (self.node_name)
        return self.execute_okc_cmd(startup_cmd)

    def kill_okc_peer(self):
        kill_cmd = "ps aux | grep %s | grep -v grep | awk '{print $2}' | xargs kill -TERM" % (self.node_name)
        return self.execute_cmd(kill_cmd)

    def save_data_dir(self):
        cmd = "tar czvf /tmp/`date +%Y%m%d_%H%M%S`.tar.gz"

    def cleanup_data_dir(self):
        cmd = "rm -rf ${OKCHAIN_PEER_DATADIR}"
        return self.execute_okc_cmd(cmd)

    def force_clean_env(self):
        cmd = "ps aux | grep -v grep | grep -v watch  | grep node | grep start | awk '{print $2}' | xargs kill -9"
        self.execute_cmd(cmd)
        time.sleep(0.2)
        cmd = "rm -rf ${OKCHAIN_DEV_DATA_TOP}"
        self.execute_okc_cmd(cmd)

    def _set_cpu_nice(self, nice=0):
        cmd = "pid=`ps aux | grep %s | grep -v grep | awk '{print $2}'`; renice -n %d -p $pid" % (self.node_name, nice)
        return self.execute_cmd(cmd)

    def decrease_priority(self):
        return self._set_cpu_nice(10)

    def set_origin_priority(self):
        return self._set_cpu_nice(0)

    def check_okc_peer_count(self, expected_count):
        cmd = self._get_process_count_cmd(self.node_name)
        std_out_text, std_err_text = self.execute_cmd(cmd)
        return int(std_out_text) == expected_count

    def okc_set_primary(self, ds_leader_address):
        ds_grpc_address = "%s:%d" % (self.host, self.grpc_port)
        cmd = "${PEER_CLIENT_BINARY} notify setprimary %s %s" % (ds_grpc_address, ds_leader_address)
        return self.execute_okc_cmd(cmd)

    def okc_startpow(self):
        grpc_address = "%s:%d" % (self.host, self.grpc_port)
        cmd = "${PEER_CLIENT_BINARY} notify startpow %s" % (grpc_address)
        return self.execute_okc_cmd(cmd)

    @utils.log_input_output
    def okc_send_transaction(self, hexFrom=None, hexTo=None, amount=0, nonce=0, count=1):
        cmd = "nohup ${OKCLI_BINARY} account transfer --from %s --to %s --amount %d --nonce %s --sendn %d --password %s --url http://%s  &" % (
            hexFrom, hexTo, amount, nonce, count, "okchain", "%s:%d" % (self.host, self.jrpc_port)
        )
        return self.execute_okc_cmd(cmd)

    @utils.log_input_output
    def okc_peercli_cmd(self, cmd_str, *args, **kwargs):
        cmd = '${OKCLI_BINARY} '
        cmd += cmd_str

        kwargs["url"] = "http://%s:%s" % (self.host, self.jrpc_port)

        for i in args:
            cmd += ' ' + str(i)

        for k, v in kwargs.items():
            cmd += ' --' + str(k) + ' ' + str(v)

        cmd = cmd.strip()
        cmd = cmd.replace('_', '').replace('PEERCLIENTBINARY', 'PEER_CLIENT_BINARY')
        print(cmd)
        return self.execute_okc_cmd(cmd)

    @utils.log_input_output
    def okc_account_create(self, *args, **kwargs):
        return self.okc_peercli_cmd('account create', *args, **kwargs)

    @utils.log_input_output
    def okc_account_info(self, *args, **kwargs):
        return self.okc_peercli_cmd('account info', *args, **kwargs)

    @utils.log_input_output
    def okc_account_keyinfo(self, *args, **kwargs):
        return self.okc_peercli_cmd('account info --key', *args, **kwargs)

    @utils.log_input_output
    def okc_account_import(self, *args, **kwargs):
        return self.okc_peercli_cmd('account import', *args, **kwargs)

    @utils.log_input_output
    def okc_account_list(self, *args, **kwargs):
        return self.okc_peercli_cmd('account list', *args, **kwargs)

    @utils.log_input_output
    def okc_account_transfer_online(self, *args, **kwargs):
        return self.okc_peercli_cmd('account transfer', *args, **kwargs)

    @utils.log_input_output
    def okc_account_transfer_offline(self, *args, **kwargs):
        return self.okc_peercli_cmd('account transfer --offline', *args, **kwargs)

    @utils.log_input_output
    def okc_account_create_with_money(self, *args, **kwargs):
        return self.okc_peercli_cmd('account create --givememoney', *args, **kwargs)

    @utils.log_input_output
    def okc_transaction_query(self, *args, **kwargs):
        return self.okc_peercli_cmd('transaction query', *args, **kwargs)

    @utils.log_input_output
    def okc_transaction_submit(self, *args, **kwargs):
        return self.okc_peercli_cmd('transaction submit', *args, **kwargs)

    @utils.log_input_output
    def okc_remove_keystore_file(self, address):
        address_str = address[2:].lower()
        cmd = '''rm $HOME/.okchain/keystore/*%s''' %address_str
        print(cmd)
        return self.execute_okc_cmd(cmd)

    def close(self):
        self._ssh.close()


class BaseNode(object):

    def __init__(self,
                 host="0.0.0.0",
                 init_peer_role="miner",
                 jrpc_port=26000,
                 grpc_port=25000,
                 init_ds_leader_addr="0.0.0.0:25000",
                 startup_ds_addresses=[],
                 startup_lookup_addresses=[],
                 sharding_size=5,
                 enable_pprof=False,
                 default_user="root"):

        self.node_name = "okc_%s_g%d_j%d" % (init_peer_role, grpc_port, jrpc_port)
        self.grpc_addr = "%s:%d" % (host, grpc_port)
        self.jrpc_addr = "http://%s:%d" % (host, jrpc_port)
        self._grpc_client = RpcClient(host, grpc_port)
        self._okc_ssh_client = OKCSSHClient(host, 22,
                                            jrpc_port, grpc_port,
                                            startup_lookup_addresses,
                                            startup_ds_addresses,
                                            init_peer_role,
                                            self.node_name,
                                            init_ds_leader_addr,
                                            sharding_size=sharding_size,
                                            enable_pprof=enable_pprof,
                                            default_user=default_user)
        self._init_ds_leader_addr = init_ds_leader_addr

    def __repr__(self):
        return "%s %s" % (self.grpc_addr, self.node_name)

    def get_grpc_client(self):
        return self._grpc_client

    def get_ssh_client(self):
        return self._okc_ssh_client

    def set_primary(self):
        return self._okc_ssh_client.okc_set_primary(self._init_ds_leader_addr)

    def start_pow(self):
        return self._okc_ssh_client.okc_startpow()

    def send_transactions(self, hexFrom="", hexTo="", amount=0, start_nonce=-1, count=1):
        if start_nonce == -1:
            trxs = self._grpc_client.GetTransactionsByAccount(hexFrom).transactions
            max_nonce = 0
            for trx in trxs:
                if trx.Nonce > max_nonce:
                    max_nonce = trx.Nonce
            start_nonce = max_nonce

        self._okc_ssh_client.okc_send_transaction(hexFrom, hexTo, amount, nonce=start_nonce, count=count)

    def echo(self, a="a", b="b"):
        return "%s:%s" % (a, b)

    @utils.log_input_output
    def apply_op(self, op_name, **op_kwargs):
        try:
            op = getattr(self, op_name)
        except Exception as e:
            try:
                op = getattr(self.get_grpc_client(), op_name)
            except Exception as e:
                try:
                    op = getattr(self.get_ssh_client(), op_name)
                except Exception as e:
                    op = None

        return op(**op_kwargs)

    def get_latest_DsBlockNum(self):
        ds_blk = self.get_grpc_client().GetLatestDsBlock()
        return ds_blk.header.blockNumber

    def get_latest_TxBlockNum(self):
        ds_blk = self.get_grpc_client().GetLatestTxBlock()
        return ds_blk.header.blockNumber

    def GetNetworkInfo(self):
        r = self.get_grpc_client().GetNetworkInfo()
        return r

    def GetPeerStatus(self):
        return self.get_grpc_client().GetPeerStatus()

    @utils.log_input_output
    def CreateAccount(self, **kwargs):
        stdout, std_error = self.get_ssh_client().okc_account_create(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_input_output
    def CreateAccountWithMoney(self, **kwargs):
        stdout, std_error = self.get_ssh_client().okc_account_create_with_money(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def KeyAccountInfo(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_account_keyinfo(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def AccountInfo(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_account_info(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def RemoveKeystoreFile(self, **kwargs):
        return self.get_ssh_client().okc_remove_keystore_file(**kwargs)

    @utils.log_exception
    def AccountImport(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_account_import(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def AccountList(self):
        stdout, stderr = self.get_ssh_client().okc_account_list()
        r = stdout.split('\n')
        return r

    @utils.log_exception
    def AccountTransferOnline(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_account_transfer_online(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def AccountTransferOffline(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_account_transfer_offline(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def TransactionQuery(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_transaction_query(**kwargs)
        r = json.loads(stdout)
        return r

    @utils.log_exception
    def TransactionSubmit(self, **kwargs):
        stdout, stderr = self.get_ssh_client().okc_transaction_submit(**kwargs)
        r = json.loads(stdout)
        return r
