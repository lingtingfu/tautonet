import unittest

from autonet.tcase import AutoCase

class MySampleCase(unittest.TestCase):

    case_name = "sample"

    def test_AutoCase(self):
        ac = AutoCase(case_name=self.case_name)
        grp_results = ac.run()
        assert grp_results != None, grp_results

        print(grp_results)

    def test_AutoCase_Cleanup(self):
        ac = AutoCase(case_name=self.case_name)
        ac.prepare()
        ac.force_clean_env()

    def test_AutoCase_handle_kwargs_with_cached_variables(self):
        cached_vars = {"b1" : 100}
        kwargs1 = {"password" : "`b1`"}
        kwargs2 = {"password" : "b1"}
        r1 = AutoCase.handle_kwargs_with_cached_variables(cached_vars, kwargs1)
        r2 = AutoCase.handle_kwargs_with_cached_variables(cached_vars, kwargs2)
        assert r1 != None and r1["password"] == 100, r1
        assert r2 != None and r2["password"] == "b1", r2

if __name__ == '__main__':
    unittest.main()
