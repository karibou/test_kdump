#!/usr/bin/python3
# Copyright 2014-2015 Canonical Limited.
#
# This file is shamelesly ripped out of charm-helpers templating.py.
#
# charm-helpers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3 as
# published by the Free Software Foundation.
#
# You should have received a copy of the GNU Lesser General Public License
# along with charm-helpers.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse


def render(source, target, context, templates_dir=None, encoding='UTF-8'):
    """
    Render a template.

    The `source` path, if not absolute, is relative to the `templates_dir`.

    The `target` path should be absolute.

    The context should be a dict containing the values to be replaced in the
    template.

    If omitted, `templates_dir` defaults to the `templates` folder.

    Note: Using this requires python-jinja2
    """
    try:
        from jinja2 import FileSystemLoader, Environment, exceptions
    except ImportError:
        print("Need to install python3-jinja2")
        sys.exit(1)

    if os.path.exists(target) and not context['force']:
        print("File %s already exists" % target)
        return(1)

    if templates_dir is None:
        templates_dir = os.path.join('.', 'templates')
    loader = Environment(loader=FileSystemLoader(templates_dir))
    try:
        source = source
        template = loader.get_template(source)
    except exceptions.TemplateNotFound as e:
        hookenv.log('Could not load template %s from %s.' %
                    (source, templates_dir),
                    level=hookenv.ERROR)
        raise e
    content = template.render(context)
    with open(target, 'wb') as file:
        file.write(content.encode(encoding))


def parse_arguments(args):
    parser = argparse.ArgumentParser(
        description='Generate the kdump-test cloud-init script')
    parser.add_argument('-f', '--force', action='store_true',
                        help='force creation of a new script')
    parser.add_argument('-d', '--do-update', action='store_true',
                        help='force apt-get update')
    parser.add_argument('-g', '--do-upgrade', action='store_true',
                        help='force apt-get upgrade')
    parser.add_argument('-p', '--use-proxy', action='store_true',
                        help='Enable local proxy')
    parser.add_argument('-o', '--output-file', nargs=1, default=['test-kdump'],
                        help='Output filename (default: test-kdump')
    args = vars(parser.parse_args())
    return(args)


if __name__ == '__main__':
    context = parse_arguments(sys.argv[1:])

    target = os.path.join(os.getenv('PWD'), context['output_file'][0])
    render('test-kdump', target, context)
