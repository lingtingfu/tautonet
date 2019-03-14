# -*- coding: utf-8 -*-
# @Time    : 2018/11/19 下午1:11
# @Author  : lingting.fu
# @Email   : lingting.fu@okcoin.com
# @File    : tclient.py
# @Software: TAutoNet

import sys
import os
import json
import datetime
from autonet import tcase

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage.$ tautonet [run|force_clean|run_conf] [case_name|all|conf.json]"
        print "case_name.expect & case_name.input is supported to be located in /opt/tautonet/tcases/, " \
              "and the test result sample.out is located in /opt/tautonet/tcases/output"
        exit()

    cmd_name = sys.argv[1]
    case_or_conf_name = sys.argv[2]

    result_map = {}
    summary_map = {}
    all_cases = []

    if cmd_name == "force_clean":
        ac = tcase.AutoCase(case_name=case_or_conf_name)
        ac.prepare()
        ac.force_clean_env()
        ac.tear_down()
    elif cmd_name == "run":
        if case_or_conf_name != "all":
            all_cases.append(case_or_conf_name)
        else:
            d = "/opt/tautonet/tcases/"
            if os.path.isdir(d):
                l = os.listdir(d)
                cases = map(lambda x: x.replace(".input", ""), filter(lambda x: x.endswith(".input"), l))
                for c in cases:
                    all_cases.append(c)
    elif cmd_name == "run_conf":
        fpath = "/opt/tautonet/tcases/" + case_or_conf_name
        with open(fpath, "r") as f:
            txt = f.read()
            all_cases = json.loads(txt)
    else:
        print("%s Not Supported." % (sys.argv))
        exit()

    # Run all cases and collect result here.
    for c in all_cases:
        ac = tcase.AutoCase(case_name=c)
        result = ac.run()
        result_map[c] = result
        print(result)

    for c, r in result_map.items():
        item_results = r
        success_cnt = len(filter(lambda x: x[1] == "PASS", item_results.items()))
        fail_cnt = len(item_results) - success_cnt
        summary_map[c] = {"ALL": len(item_results), "PASS": success_cnt, "FAIL": fail_cnt}

    summary_text = json.dumps(summary_map, indent=4)
    fname = d + os.path + "Summary_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(fname, "w") as f:
        f.write(summary_text)

    print(summary_text)
