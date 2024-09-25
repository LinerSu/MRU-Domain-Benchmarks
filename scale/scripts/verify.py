#!/usr/bin/env python3

import os
import os.path
import sys

CLAM_DIR = '/home/agent/tools/clam'
CLAMYAML_DIR = 'run/bin/clam-yaml.py'

def add_help_arg (ap):
    ap.add_argument('-h', '--help', action='help',
                    help='Print this message and exit')

class CliCmd (object):
    def __init__ (self, name='', help='', allow_extra=False):
        self.name = name
        self.help = help
        self.allow_extra = allow_extra

    def mk_arg_parser (self, argp):
        add_help_arg (argp)
        return argp

    def run (self, args=None, extra=[]):
        return 0

    def name_out_file (self, in_files, args=None, work_dir=None):
        out_file = 'out'
        if work_dir is not None:
            out_file = os.path.join (work_dir, out_file)
        return out_file

    def main (self, argv):
        import argparse
        ap = argparse.ArgumentParser (prog=self.name,
                                      description=self.help,
                                      add_help=False)
        ap = self.mk_arg_parser (ap)

        if self.allow_extra:
            args, extra = ap.parse_known_args (argv)
        else:
            args = ap.parse_args (argv)
            extra = []
        return self.run (args, extra)


def main(argv):

    class VerifyCmd(CliCmd):
        def __init__(self):
            super().__init__('verify', 'Verify', allow_extra=True)

        def mk_arg_parser(self, argp):
            import argparse
            argp = super().mk_arg_parser(argp)

            argp.add_argument('-v', '--verbose', action='store_true',
                              default=False)
            argp.add_argument('--mem-dom', dest='mem_dom', type=str, default='obj',
                              help='Select what type of domain')
            argp.add_argument('--reduce-option', dest='reduce_option', type=str, default=None,help='Select what type of reduction')
            argp.add_argument('--silent', action='store_true', default=False,
                              help='Do not produce any output')
            argp.add_argument('--expect', type=str, default=None,
                              help='Expected string in the output')
            argp.add_argument('--null', action='store_true', default=False,
                              help='Check null dereference')
            argp.add_argument('--uaf', action='store_true', default=False,
                              help='Check use-after-free')
            argp.add_argument('--bounds', action='store_true', default=False,
                              help='Check buffer overflow')
            argp.add_argument('--isderef', action='store_true', default=False,
                              help='Check is-deref assertions')
            argp.add_argument('--nocheck', action='store_true', default=False,
                              help='No safety property check, dry run')
            argp.add_argument('input_file', nargs=1)
            argp.add_argument('--dry-run', dest='dry_run',
                              action='store_true', default=False,
                              help='Pass --dry-run to yama')
            argp.add_argument('extra', nargs=argparse.REMAINDER)
            return argp

        def run(self, args=None, _extra=[]):
            extra = _extra + args.extra

            script_dir = os.path.abspath(sys.argv[0])
            script_dir = os.path.dirname(script_dir)
            parent_dir = os.path.dirname(script_dir)
            yaml_dir = os.path.join(parent_dir, 'yaml')

            input_file = os.path.abspath(args.input_file[0])

            file_dir = input_file
            file_dir = os.path.dirname(file_dir)

            if args.mem_dom == 'obj' :
                build_dir = 'build'
            elif args.mem_dom == 'rgn' :
                build_dir = 'build_rgn'
            else:
                sys.exit(-1)
                
            if not os.path.exists(CLAM_DIR):
                print(f'CLAM directory not found: {CLAM_DIR}')
                print(f'Please set the CLAM_DIR environment variable in {__file__} script.')
                sys.exit(-1)

            cmd = [os.path.join(CLAM_DIR, build_dir, 'run', 'bin', 'clam-yaml.py')]

            # base config
            base_config = os.path.join(yaml_dir, 'clam-base.yaml')
            cmd.extend(['-y', base_config])

            if args.reduce_option == 'none':
                noreduce_config = os.path.join(yaml_dir, 'mru_no_reduce.yaml')
                cmd.extend(['-y', noreduce_config])
            elif args.reduce_option == 'opt':
                optreduce_config = os.path.join(yaml_dir, 'mru_heuristic_reduce.yaml')
                cmd.extend(['-y', optreduce_config])
            elif args.reduce_option == 'full':
                fullreduce_config = os.path.join(yaml_dir, 'mru_full_reduce.yaml')
                cmd.extend(['-y', fullreduce_config])

            if args.dry_run:
                cmd.append('--dry-run')

            cmd.append(input_file)
            cmd.extend(extra)

            if args.verbose:
                print(' '.join(cmd))
   
            if args.expect is None:
                os.execv(cmd[0], cmd)

    cmd = VerifyCmd()

    return cmd.main(argv)


if __name__ == '__main__':

    sys.exit(main(sys.argv[1:]))
