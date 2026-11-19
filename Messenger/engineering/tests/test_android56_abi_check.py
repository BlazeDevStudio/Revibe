import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from android56_abi_check import classify

class Android56ABITests(unittest.TestCase):
    def test_android5_dual_abi(self):
        self.assertTrue(classify(21,["arm64-v8a","armeabi-v7a"],["armeabi-v7a"])["basic_install_eligible"])
    def test_android6_dual_abi(self):
        self.assertTrue(classify(23,["arm64-v8a","armeabi-v7a"],["armeabi-v7a"])["basic_install_eligible"])
    def test_arm64_only_fails(self):
        self.assertFalse(classify(23,["arm64-v8a"],["armeabi-v7a"])["basic_install_eligible"])
    def test_android43_fails(self):
        self.assertFalse(classify(18,["armeabi-v7a"],["armeabi-v7a"])["basic_install_eligible"])
    def test_x86_fails(self):
        self.assertFalse(classify(23,["x86"],["armeabi-v7a"])["basic_install_eligible"])
    def test_not_messaging_verified(self):
        r=classify(23,["arm64-v8a","armeabi-v7a"],["armeabi-v7a"])
        self.assertFalse(r["e2ee_messaging_verified"])
if __name__=="__main__": unittest.main()
