import unittest, sys, os, tempfile, shutil
import mock
import gentest
from jinja2 import exceptions


class gentestTests(unittest.TestCase):
    @classmethod
    def setUp(letest):
        letest.workdir = tempfile.mkdtemp()
        gentest.PWD = letest.workdir
        letest.context = {'do_upgrade': False, 'force': False,
                          'use_proxy': False, 'do_update': False,
                          'output_file': ['test-kdump'], 'distrib': ['ubuntu'],
                          'networked': False, 'result': False}

    @classmethod
    def tearDown(letest):
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

    def test_render_bad_template(self):

        self.target = os.path.join(self.workdir, 'test-kdump')
        with self.assertRaises(exceptions.TemplateNotFound) as cont:
            gentest.render('bad-template', self.target, self.context)
        self.assertEqual(cont.exception.message, 'bad-template')

    def test_render_default_boolean_options(self):

        self.context_tests = {'do_upgrade': [False, 'package_upgrade: true'],
                              'use_proxy': [False, 'apt_proxy'],
                              'do_update': [False, 'package_update: true'],
                              'networked': [True, 'LOCAL_ONLY=1'],
                              'results': [True, 'NO_RESULT=1']}
        self.context['force'] = True
        self.target = os.path.join(self.workdir, 'test-kdump')
        for self.test in self.context_tests.keys():
            self.context[self.test] = self.context_tests[self.test][0]
            self.assertEqual(gentest.render('test-kdump', self.target,
                             self.context), None)
            self.option = self.context_tests[self.test][1]
            self.assertFalse(self._is_in_file(self.target, self.option),
                             'Option "{}" not found'.format(self.option))

    def test_render_boolean_options(self):

        self.context_tests = {'do_upgrade': [True, 'package_upgrade: true'],
                              'use_proxy': [True, 'apt_proxy'],
                              'do_update': [True, 'package_update: true'],
                              'networked': [False, 'LOCAL_ONLY=1'],
                              'results': [False, 'NO_RESULT=1']}
        self.context['force'] = True
        self.target = os.path.join(self.workdir, 'test-kdump')
        for self.test in self.context_tests.keys():
            self.context[self.test] = self.context_tests[self.test][0]
            self.assertEqual(gentest.render('test-kdump', self.target,
                             self.context), None)
            self.option = self.context_tests[self.test][1]
            self.assertTrue(self._is_in_file(self.target, self.option),
                            'Option "{}" not found'.format(self.option))

    def test_render_distrib(self):

        self.distrib_tests = {'debian': 'REMOTE_USER=root',
                              'ubuntu': 'crashkernel=384M-2G:64M'}
        self.context['force'] = True
        self.target = os.path.join(self.workdir, 'test-kdump')
        for self.test in self.distrib_tests.keys():
            self.context['distrib'].pop()
            self.context['distrib'].append(self.test)
            self.assertEqual(gentest.render('test-kdump', self.target,
                             self.context), None)
            self.option = self.distrib_tests[self.test]
            self.assertTrue(self._is_in_file(self.target, self.option),
                            'Option "{}" not found'.format(self.option))
