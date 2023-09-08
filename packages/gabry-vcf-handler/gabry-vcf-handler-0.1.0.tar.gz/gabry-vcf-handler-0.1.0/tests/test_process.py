from src.process import process_vcf
from logging import Logger
import unittest


def test_process_vcf():
    log = Logger("logger")
    assert process_vcf("tests/data/test.vcf", "tests/data/test.csv", log) == "Hello World"


class TestProcessLogs(unittest.TestCase):
    def test_process_vcf_logs(self):
        test_log = Logger("test_logger")
        with self.assertLogs(test_log, level="INFO") as cm:
            process_vcf("tests/data/test.vcf", "tests/data/test.csv", test_log)
            self.assertEqual(cm.output, ["INFO:test_logger:Hello World"])
