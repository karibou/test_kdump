#!/usr/bin/python3
# Copyright 2014-2015 Canonical Limited.
#
# You should have received a copy of the GNU Lesser General Public License
# along with charm-helpers.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse


# This function is shamelesly ripped out of charm-helpers templating.py.
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
    loader = Environment(loader=FileSystemLoader(templates_dir),
                         lstrip_blocks=True, trim_blocks=True)
    try:
        source = source
        template = loader.get_template(source)
    except exceptions.TemplateNotFound as e:
        print('Could not load template %s from %s.' %
              (source, templates_dir))
        raise e
    content = template.render(context)
    with open(target, 'wb') as file:
        file.write(content.encode(encoding))


def validate_ppa(url):

    if url == None:
        raise ValueError

    if url[0][:3] != 'ppa':
        print("Invalid PPA format (missing ppa: prefix) : %s" % url[0])
        return(1)

    if url[0].find('/') == -1:
        print("Invalid PPA format (missing /{ppa} name) : %s" % url[0])
        return(1)
    return(0)

def parse_arguments(args):
    """
    Valid arguments are :

    --force | -f       : Force overwriting of an existing script

    --do-update | -d   : Do apt-get update when starting instance

    --do-upgrade | -g  : Do apt-get upgrade when starting instance

    --use-proxy | -p   : Use a local proxy

    --ppa | -P         : Use the provided PPA as an archive source

    --output-file | -o : Override the default output file (test-kdump)

    --distrib | -D     : Override the default distribution to be generated
                         (ubuntu)

    --network | -n     : Do networked kernel dump capture tests.
                         (default: local test only)

    --result | -r      : Verify resulting crash dumps (much longer)
                         (default: do not verify results)
    """
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
    parser.add_argument('-P', '--ppa', nargs=1,
                        help='Provide a PPA to be used for the test')
    parser.add_argument('-o', '--output-file', nargs=1, default=['test-kdump'],
                        help='Output filename (default: test-kdump')
    parser.add_argument('-D', '--distrib', nargs=1, default=['ubuntu'],
                        choices=['ubuntu', 'debian'],
                        help='Distribution specific config (default: ubuntu)')
    parser.add_argument('-n', '--networked', action='store_true',
                        help='Enable remote kernel dumps (default: local only')
    parser.add_argument('-r', '--results', action='store_true',
                        help='Verify resulting kernel dumps (much longer)')
    args = vars(parser.parse_args())

    if args['ppa'] is not None:
        if validate_ppa(args['ppa']):
            return(1)
        else:
            return(args)


if __name__ == '__main__':
    context = parse_arguments(sys.argv[1:])

    if isinstance(context, dict):
        target = os.path.join(os.getenv('PWD'), context['output_file'][0])
        render('test-kdump', target, context)
