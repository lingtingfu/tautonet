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
        print "usage.$ tautonet [run|force_clean] case_name"
        print "case_name.expect & case_name.input is supported to be located in /opt/tautonet/tcases/, and the test result sample.out is located in /opt/tautonet/tcases/output"
        exit()

    cmd_name = sys.argv[1]
    case_name = sys.argv[2]
    if cmd_name == "force_clean":
        ac = tcase.AutoCase(case_name=case_name)
        ac.prepare()
        ac.force_clean_env()
        ac.tear_down()
    elif cmd_name == "run":
        if case_name != "all":
            ac = tcase.AutoCase(case_name=case_name)
            result = ac.run()
            print(result)
        else:
            d = "/opt/tautonet/tcases/"
            if os.path.isdir(d):
                l = os.listdir(d)
                cases = map(lambda x: x.replace(".input", ""), filter(lambda x: x.endswith(".input"), l))
                result_map = {}
                summary_map = {}
                for c in cases:
                    ac = tcase.AutoCase(case_name=case_name)
                    result = ac.run()
                    result_map[c] = result

                for c, r in result_map.items():
                    item_results = json.loads(r)
                    success_cnt = len(filter(lambda x: x[1] == "PASS", item_results.items()))
                    fail_cnt = len(item_results) - success_cnt
                    summary_map[c] = {"ALL" : len(item_results), "PASS" : success_cnt, "FAIL" : fail_cnt}

                summary_text = json.dumps(summary_map, indent=4)
                fname = d + os.path + "Summary_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(fname, "w") as f:
                    f.write(summary_text)

                print(summary_text)
    else:
        print("%s Not Supported." % (sys.argv))