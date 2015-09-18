import unittest, sys, os, tempfile, shutil
import mock
import gentest


class gentestTests(unittest.TestCase):
    @classmethod
    def setUpClass(letest):
        letest.workdir = tempfile.mkdtemp()
        gentest.PWD = letest.workdir
        letest.context = {'do_upgrade': False, 'force': False,
                          'use_proxy': False, 'do_update': False,
                          'output_file': ['test-kdump']}

    @classmethod
    def tearDownClass(letest):
        shutil.rmtree(letest.workdir)


