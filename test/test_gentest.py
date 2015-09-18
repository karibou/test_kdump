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

    def test_render_exists(self):
        self.target = os.path.join(self.workdir, 'test-kdump')
        # create pre-existing file
        with open(self.target, 'w') as target:
            target.write('a')

        self.assertEqual(gentest.render('test-kdump', self.target,
                         self.context), 1)
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, 'File %s already exists' % self.target)

    def test_render_exists_with_force(self):
        self.target = os.path.join(self.workdir, 'test-kdump')
        # create pre-existing file
        with open(self.target, 'w') as target:
            target.write('a')

        self.context['force'] = True
        self.assertEqual(gentest.render('test-kdump', self.target,
                         self.context), None)

    def test_render_with_filename(self):

        self.context['output_file'] = 'testfile'
        self.target = os.path.join(self.workdir, 'testfile')
        self.assertEqual(gentest.render('test-kdump', self.target,
                         self.context), None)
        self.assertTrue(os.path.exists(self.target))
