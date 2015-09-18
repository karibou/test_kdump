import unittest, sys, os
import mock
import gentest


class gentestTests(unittest.TestCase):
    @classmethod
    def setUpClass(letest):
        pass

    @classmethod
    def tearDownClass(letest):
        pass

    def test_parser(self):
        args = mock.Mock()

        mock.patch('parser.parse_args')
        args.call_args = ['--force', '--do-update', '--do-upgrade', '--use-proxy']
        self.context = gentest.parse_arguments(args.call_args)
        # self.assertTrue(context['force'])
