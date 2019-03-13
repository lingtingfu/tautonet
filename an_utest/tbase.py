# -*- coding: UTF-8 -*-
import unittest

from autonet.tbase import RpcClient, OKCSSHClient, OKCConst, BaseNode
import time

URL = "http://192.168.168.23:16001"
PASSWORD_1 = "dianfengshan"
PASSWORD_2 = "gejiucai"
BASE_NODE_CONFIG = dict(host="192.168.168.22", grpc_port=25000, jrpc_port=26000,
                        init_ds_leader_addr="192.168.168.22:25000", sharding_size=7)

class MyTestCase(unittest.TestCase):
    test_from_addr = "4ba6fa234186ff7db0c10faa103eecb02a4f26fb"
    test_to_addr = "d8104e3e6de811dd0cc07d32ccce2f4f4b38403a"

    def test_rpc_block_smoke(self):
        rclient = RpcClient("192.168.168.107", 15009)
        dsBlock = rclient.GetLatestDsBlock()
        assert dsBlock != None, dsBlock

        txBlock = rclient.GetLatestTxBlock()
        assert txBlock != None, txBlock

        dsBlock = rclient.GetLatestDsBlock()
        assert dsBlock != None, dsBlock

        networks = rclient.GetNetworkInfo()
        print(len(networks.DsList), len(networks.ShardingList), len(networks.LookupList), len(networks.RemotePeerList))
        assert networks != None and len(networks.RemotePeerList) > 0, networks
        print(dsBlock, txBlock, networks)

        time.sleep(2)
        peerStatus = rclient.GetPeerStatus()
        assert peerStatus != None, peerStatus
        print(peerStatus)

        rclient.close()

    def test_rpc_transaction_smoke(self):
        rclient = RpcClient("127.0.0.1", 15009)

        accountResp = rclient.GetAccount(MyTestCase.test_from_addr)
        print(accountResp.account)
        print(accountResp.account.Nonce)

        all_trxs = rclient.GetTransactionsByAccount(MyTestCase.test_from_addr)
        print(all_trxs)

        r = rclient.SendTransaction(
            hexFromAddr=MyTestCase.test_from_addr,
            hexToAddr=MyTestCase.test_to_addr,
            amount=100,
            nonce=8
        )
        print(r.hash)

        all_trxs = rclient.GetTransactionsByAccount(MyTestCase.test_from_addr)
        print(all_trxs)

        rclient.close()

    def test_ssh_run_okchain_cmd(self):
        node_name = "utest_node_test"
        # sshclient = OKCSSHClient("127.0.0.1", 22, 26060, 25060, ["192.168.168.22:25001"], ["192.168.168.22:25001"], OKCConst.PEER_ROLE_MINER, node_name, "192.168.168.22:25001")
        sshclient = OKCSSHClient("127.0.0.1", 22, 26060, 25060, ["127.0.0.1:25001"], ["127.0.0.1:25001"], OKCConst.PEER_ROLE_MINER, node_name, "127.0.0.1:25001", default_user="lingting.fu")
        print(sshclient.execute_okc_cmd( "export"))
        print(sshclient.kill_okc_peer())
        print(sshclient.start_okc_peer())
        time.sleep(2)

        print(sshclient.okc_send_transaction(self.test_from_addr, self.test_to_addr, 100, 1))

        print(sshclient.execute_cmd("sleep 1; ps aux | grep %s | grep -v grep" % node_name))
        assert sshclient.check_okc_peer_count(1)

        print(sshclient.okc_set_primary("192.168.168.22:25001"))
        print(sshclient.execute_cmd("sleep 3;"))

        print(sshclient.kill_okc_peer())
        print(sshclient.execute_cmd("sleep 0.3; ps aux | grep %s | grep -v grep" % node_name))
        assert sshclient.check_okc_peer_count(0)
        print(sshclient.execute_cmd("ps aux | grep %s | grep -v grep" % node_name))


    def test_dict(self):
        d = {"a" : 100, "b" : "1999"}
        t = '''
            %(a)s
        ''' % d
        print(t)

    def test_base_node(self):
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()
        time.sleep(3)

        stdout_txt, stderr_txt = node.set_primary()
        assert stderr_txt == None or len(stderr_txt) == 0 or 'panic' not in stderr_txt, stderr_txt
        print(stdout_txt, stderr_txt)

        time.sleep(5)

        # stdout_txt, stderr_txt = node.get_ssh_client().kill_okc_peer()
        # assert stderr_txt == None or len(stderr_txt) == 0 or 'panic' not in stderr_txt, stderr_txt
        # print(stdout_txt, stderr_txt)


    def test_create_account(self):
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()
        res = node.CreateAccount(password=PASSWORD_1)
        print(res)
        assert res is not None and isinstance(res, dict) and ("Address" in res) and ("Mnemonic" in res) and (
            "PrivateKey" in res)

    def test_account_info(self):
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()
        account = node.CreateAccount(password=PASSWORD_1)
        address = account['Address']
        res = node.AccountInfo(addr=address, password=PASSWORD_1, url=URL)
        print(res)
        assert res is not None and isinstance(res, dict) and res['Nonce'] == 0 and res['Balance'] == 0

    def test_account_keyinfo(self):
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()
        account = node.CreateAccount(password=PASSWORD_1)
        address = account['Address']
        res = node.KeyAccountInfo(addr=address, password=PASSWORD_1)
        print(res)
        assert res is not None and isinstance(res, dict) and ("Address" in res) and (
                "PublicKey" in res) and ("PrivateKey" in res) and res['Address'] == address

    def test_account_import(self):
        # 1. Start a Node
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()

        # 2. Create an Account
        account = node.CreateAccount(password=PASSWORD_1)
        address = account['Address']
        mnemonic = '"' + account['Mnemonic'] + '"'
        private_key = account['PrivateKey']

        # 3. Remove Keystore File
        node.RemoveKeystoreFile(address=address)

        # 4. Import the account by private key
        res = node.AccountImport(privatekey=private_key, password=PASSWORD_1)
        print(res)
        assert res is not None and isinstance(res, dict) and res['Address'].lower() == address.lower()

        # 5. Remove Keystore File Again
        node.RemoveKeystoreFile(address=address)

        # 6. Import the account by mnemonic seed
        res = node.AccountImport(mnemonic=mnemonic, password=PASSWORD_1)
        print(res)
        assert res is not None and isinstance(res, dict) and res['Address'].lower() == address.lower()

    def test_account_list(self):
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()
        account = node.CreateAccount(password=PASSWORD_1)
        address = account['Address']
        res = node.AccountList()
        print(res[-2], address[2:].lower())
        assert (res is not None) and isinstance(res, list) and isinstance(res[0], str) and (address[2:].lower() in res[-2])

    def test_account_transfer_online(self):
        # 1. Start a Node
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()

        # 2. Create an Account with money
        account_a = node.CreateAccountWithMoney(password=PASSWORD_1, url=URL)
        address_a = account_a['Address']
        time.sleep(30)

        # 3. Create another account
        account_b = node.CreateAccount(password=PASSWORD_2)
        address_b = account_b['Address']

        # 4. Transfer money online
        tx = node.AccountTransferOnline(amount=100000, _from=address_a, to=address_b, nonce=0, password=PASSWORD_1,
                                    url=URL, gasPrice=1)
        print(tx)
        assert isinstance(tx, list) and isinstance(tx[0], dict) and ('TransactionId' in tx[0]) and len(tx[0]['TransactionId']) == 66

        # 5. Query Transaction online
        txid = tx[0]['TransactionId']
        tx_info = node.TransactionQuery(txid=txid, url=URL)
        assert isinstance(tx_info, dict) and ("blockNumber" in tx_info)

        time.sleep(90)
        tx_info = node.TransactionQuery(txid=txid, url=URL)
        assert isinstance(tx_info, dict) and ("blockNumber" in tx_info) and tx_info["blockNumber"] > 0

    def test_account_transfer_offline(self):
        # 1. Start a Node
        node = BaseNode(**BASE_NODE_CONFIG)
        node.get_ssh_client().start_okc_peer()

        # 2. Create an Account with money
        account_a = node.CreateAccountWithMoney(password=PASSWORD_1, url=URL)
        address_a = account_a['Address']
        time.sleep(30)

        # 3. Create another account
        account_b = node.CreateAccount(password=PASSWORD_2)
        address_b = account_b['Address']

        # 4. Transfer money offline
        tx = node.AccountTransferOffline(amount=100000, _from=address_a, to=address_b, nonce=0, password=PASSWORD_1,
                                    url=URL, gasPrice=1)
        print(tx)
        assert isinstance(tx, list) and isinstance(tx[0], dict) and (
                'TransactionId' in tx[0]) and len(tx[0]['TransactionId']) == 66

        # 5. Query Transaction
        txid = tx[0]['TransactionId']
        tx_info = node.TransactionQuery(txid=txid, url=URL)
        assert tx_info is None

        # 6. Submit Transaction
        StoreFile = tx[0]['StoreFile']
        tx = node.TransactionSubmit(signedtx=StoreFile, url=URL)
        assert isinstance(tx, dict) and ('TransactionHash' in tx) and len(
            tx['TransactionHash']) == 66

        # 7. Query Transaction
        txid = tx['TransactionHash']
        time.sleep(90)
        tx_info = node.TransactionQuery(txid=txid, url=URL)
        assert isinstance(tx_info, dict) and ("blockNumber" in tx_info) and tx_info["blockNumber"] > 0


if __name__ == '__main__':
    unittest.main()
