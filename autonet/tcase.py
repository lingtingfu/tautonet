# -*- coding: utf-8 -*-
# @Time    : 2018/11/12 上午11:42
# @Author  : lingting.fu
# @Email   : lingting.fu@okcoin.com
# @File    : tcase.py
# @Software: TAutoNet

from autonet.tnet import TAutoNet
from autonet.utils import log_traceback_str, log_exception, LOG, log_input_output

import json
import os
import time
from threading import Thread

class AutoCase(object):

    CHECK_GROUP_MODE_AND = "&"
    CHECK_GROUP_MODE_OR = "|"
    CHECK_RESULT_PASS = "PASS"
    CHECK_RESULT_FAIL = "FAIL"

    HOST_MAP = {}

    @log_input_output
    def __locate_tcase_dir(self, case_dir=None):
        if case_dir != None:
            return case_dir
        else:
            p = os.path.abspath(__file__) + "../tcases/"
            for x in [p, "/opt/tautonet/tcases"]:
                if os.path.exists(x):
                    return x

    def __init__(self, case_dir=None, case_name="sample"):
        self._case_dir = self.__locate_tcase_dir(case_dir)
        self._case_file = self._case_dir + os.sep + case_name + ".input"
        self._expect_file = self._case_dir + os.sep + case_name + ".expect"
        self._output_dir = self._case_dir + os.sep + "output"
        self._output_file = self._output_dir + os.sep + case_name + ".output"
        self._hostname_file = self._case_dir + os.sep + "hostnames.json"

        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir, mode=744)

        with open(self._case_file, "r") as f:
            case_desc_text = f.read()
            self._case_desc = json.loads(case_desc_text)

        with open(self._expect_file, "r") as f:
            expect_desc_text = f.read()
            self._expect_desc = json.loads(expect_desc_text)

        with open(self._hostname_file, "r") as f:
            hostname_text = f.read()
            self.HOST_MAP = json.loads(hostname_text)

        self._network_desc = self._case_desc["network_desc"]
        self._network = None

    def run(self):
        self.prepare()
        self.setup()
        self.apply_ops()
        check_reslut = self.check_output()
        self.tear_down()
        return check_reslut

    def force_clean_env(self):
        self._network.force_clean_env()

    def __get_apply_nodes_by_group(self, grp):
        role_or_addr_list = grp.split(",")
        if "*" in role_or_addr_list:
            return self._network.get_all_nodes()

        nlist = []
        for x in role_or_addr_list:
            nodes = self._network.locate_nodes(x)
            nlist = nlist + nodes

        return nlist

    # @log_input_output
    def __get_check_nodes_by_group(self, grp_list_str):
        '''
        Support only single mode: '&' or '|'
        :param grp_list_str:  'ds&miner&lookup' or  '192.168.168.22:25100|192.168.168.22:25100'
        :return:
        '''
        grps_and = grp_list_str.split(self.CHECK_GROUP_MODE_AND)
        grps_or = grp_list_str.split(self.CHECK_GROUP_MODE_OR)
        assert len(grps_and) == 1 or len(grps_or)
        grp_list = grps_and if len(grps_and) >= len(grps_or) else grps_or
        mode = self.CHECK_GROUP_MODE_AND if len(grps_and) >= len(grps_or) else grps_or

        nset = set()
        for x in grp_list:
            nodes = self._network.locate_nodes(x)
            [nset.add(n) for n in nodes]

        return sorted(list(nset)), mode

    def prepare(self):
        self._network = TAutoNet(self._network_desc)
        self._network.network_refresher.start()

    def __apply_simple_actions(self, actions):
        for act in actions:
            wait_after_action, repeat, node_groups, op, op_kwargs = act
            if node_groups == "#":
                nw = self._network
                nw.apply_op(op, **op_kwargs)
            else:
                n_list = self.__get_apply_nodes_by_group(node_groups)
                for i in xrange(0, repeat):
                    for n in n_list:
                        n.apply_op(op, **op_kwargs)

                if "kill" in op:
                    for n in n_list:
                        self._network.remove_killed_node(n)

            if wait_after_action > 0:
                time.sleep(wait_after_action)

    def setup(self):
        setup_actions = self._case_desc["setup_actions"]
        self.__apply_simple_actions(setup_actions)
        if self._case_desc["wait_after_setup"] > 0:
            time.sleep(self._case_desc["wait_after_setup"])

    class ApplyThread(Thread):
        def __init__(self, node, op, op_kwargs):
            self.node = node
            self.op = op
            self.op_kwargs = op_kwargs
            super(AutoCase.ApplyThread, self).__init__()

        def run(self):
            self.node.apply_op(self.op, **self.op_kwargs)

    @log_exception
    def apply_ops(self):
        apply_actions = self._case_desc["apply_actions"]
        for act in apply_actions:
            wait_after_action, repeat, node_groups, op, op_kwargs, apply_in_single_thread = act

            if node_groups == "#":
                self._network.apply_op(op, **op_kwargs)

            else:
                n_list = self.__get_apply_nodes_by_group(node_groups)
                if n_list == None or len(n_list) == 0:
                    continue

                for i in xrange(0, repeat):
                    for n in n_list:
                        if apply_in_single_thread:
                            t = AutoCase.ApplyThread(n, op, op_kwargs)
                            t.start()
                        else:
                            n.apply_op(op, **op_kwargs)

            if wait_after_action > 0:
                time.sleep(wait_after_action)

        if self._case_desc["wait_after_apply"] > 0:
            time.sleep(self._case_desc["wait_after_apply"])

    @classmethod
    def handle_kwargs_with_cached_variables(cls, cachecd_variables, kwargs):
        r = {}
        r.update(kwargs)
        for k, v in kwargs.items():
            for ck, cv in cachecd_variables.items():
                if v == "`" + ck + "`":
                    r[k] = cv
                    break
        return r


    @log_exception
    def check_output(self):
        LOG.info("Network Group Map: %s" % self._network.get_crrt_network_roles_map())
        self._network.refresh_network()
        grp_results = {}
        all_cachecd_variables = {}
        for check in self._expect_desc:
            chk_result = True
            grp_result = {}
            node_results = {}
            node_grp_str, op, kwargs, logic_expression = check[0], check[1], check[2], check[3]
            cached_variables_exec = check[4] if len(check) >= 5 else None
            wait_after_check = check[5] if len(check) >= 6 else 0

            grp_result["**kwargs"] = kwargs
            try:
                node_list, check_mode = self.__get_check_nodes_by_group(node_grp_str)
                for n in node_list:
                    handled_kwargs = AutoCase.handle_kwargs_with_cached_variables(all_cachecd_variables, kwargs)
                    LOG.info("%s", str(n))
                    r = n.apply_op(op, **handled_kwargs)
                    b = eval(logic_expression)
                    if cached_variables_exec != None:
                        c = eval(cached_variables_exec)
                        if c != None and len(c) > 0:
                            all_cachecd_variables.update(c)

                    node_results["%s" % (n.grpc_addr)] = self.CHECK_RESULT_PASS if b else self.CHECK_RESULT_FAIL
                    if not b:
                        LOG.error("%s, logic_check [%s] Fail, Actually: %s" % (n.node_name, logic_expression, r))

                if check_mode == self.CHECK_GROUP_MODE_AND:
                    chk_result = len(filter(lambda x: x.endswith(self.CHECK_RESULT_PASS), node_results.values())) == len(node_list)
                elif check_mode == self.CHECK_GROUP_MODE_OR:
                    chk_result = len(filter(lambda x: x.endswith(self.CHECK_RESULT_PASS), node_results.values())) >= 1

                grp_result["details"] = node_results
                grp_result["group_chk_result"] = self.CHECK_RESULT_PASS if chk_result else self.CHECK_RESULT_FAIL

                if wait_after_check > 0:
                    time.sleep(wait_after_check)

            except Exception as e:
                if grp_result.get("EXCEPTION") == None:
                    grp_result["EXCEPTION"] = [log_traceback_str()]
                else:
                    grp_result["EXCEPTION"].append(log_traceback_str())


            grp_results["%s @@ %s @@ [%s]" % (op, node_grp_str, logic_expression)] = grp_result

        result_text = json.dumps(grp_results, indent=4, sort_keys=True)
        print("OutputFile: " + self._output_file)
        with open(self._output_file, "w") as f:
            f.write(result_text)

        return grp_results

    @log_exception
    @log_input_output
    def tear_down(self, clearup_data=False, save_context=True):
        if self._network.network_refresher != None:
            self._network.network_refresher.stop()

        self._network.shutdown_nodes()
        if clearup_data:
            self._network.cleanup_data()
            
        teardown_actions = self._case_desc["teardown_actions"]
        self.__apply_simple_actions(teardown_actions)
