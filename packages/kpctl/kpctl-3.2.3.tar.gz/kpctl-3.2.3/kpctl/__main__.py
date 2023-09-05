#!/usr/bin/python3
###############################################################################
# Copyright 2015-2023 Tim Stephenson and contributors
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file except in compliance with the License.  You may obtain a copy
#  of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations under
#  the License.
#
# Command line client for managing process application lifecycle.
#
###############################################################################
import argparse
from colorama import Fore, Back, Style
from getpass import getpass
from importlib.metadata import version
import logging
import sys

import kpctl
from kpctl.bpmn.bpmn_documenter import BpmDocumenter
from kpctl.bpmn.bpmn_editor import BpmnEditor
from kpctl.bpmn.bpmn_validator import BpmnValidator
from kpctl.exec.curl import Curl
from kpctl.configurator import Configurator
from kpctl.exec.deployer import BpmDeployer
from kpctl.exceptions import KpException
from kpctl.local_cache import cache

from kpctl.color_log_formatter import ColorFormatter

def help(parser):
    print(f'{__package__} {version(__package__)}')
    parser.print_help()

def main():
    '''Main entry point to kpctl'''

    parser = argparse.ArgumentParser(prog="kpctl", add_help=False)
    parser.add_argument("-f", "--force", help="overwrite existing files",
        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
        type=int, default=logging.WARNING, required=False)
    subparser = parser.add_subparsers(dest="cmd")

    subparser.add_parser('cache', help='cache resources used elsewhere')

    validate_parser = subparser.add_parser('validate', help='validate (esp. bpmn)')
    validate_parser.add_argument("input", help="source file or folder")

    generate_parser = subparser.add_parser('document', help='generate documentation')
    generate_parser.add_argument("input", help="source file or folder")

    impl_parser = subparser.add_parser('implement', help='generate implementation tips')
    impl_parser.add_argument("input", help="source file or folder")

    get_parser = subparser.add_parser('get', help='get a list of objects with type')
    get_parser.add_argument("type", help="object type to get")
    get_parser.add_argument("input", help="source file or folder")

    describe_parser = subparser.add_parser('describe', help='describe the specified object')
    describe_parser.add_argument("id", help="object to describe")
    describe_parser.add_argument("input", help="source file or folder")

    set_parser = subparser.add_parser('set', help='set a new value of the specified object')
    set_parser.add_argument("id", help="object to update")
    set_parser.add_argument("target", help="the part of the object being targetted")
    set_parser.add_argument("value", help="value to set")
    set_parser.add_argument("input", help="source file or folder")

    set_ext_parser = subparser.add_parser('setextension', help='set a new value of the specified object extension')
    set_ext_parser.add_argument("id", help="object to update")
    set_ext_parser.add_argument("target", help="the extension being targetted")
    set_ext_parser.add_argument("value", help="value to set")
    set_ext_parser.add_argument("input", help="source file or folder")

    set_res_parser = subparser.add_parser('setresource', help='set a resource for a task')
    set_res_parser.add_argument("id", help="task to update")
    set_res_parser.add_argument("value", help="value to set")
    set_res_parser.add_argument("input", help="source file or folder")

    package_parser = subparser.add_parser('package', help='create deployable file from source')
    package_parser.add_argument("input", help="directory containing source files")
    package_parser.add_argument("-o", "--output", help="file name for archive to create",
            default=None)

    deploy_parser = subparser.add_parser('deploy', help='deploy a deployable file to a server')
    deploy_parser.add_argument("app", help="name of application archive to deploy")
    deploy_parser.add_argument("target", help="logical name for target server (section heading of config file)")
    deploy_parser.add_argument("-u", "--user", help="user to perform deployment")
    deploy_parser.add_argument("-p", "--password", action="store_true",
            help="prompt for password to perform deployment")

    curl_parser = subparser.add_parser('curl', help='query / update server endpoints')
    curl_parser.add_argument("target", help="logical name for target server (section heading of config file)")
    curl_parser.add_argument("url", help="api url to call")
    curl_parser.add_argument("-d", "--data", help="payload, if expected by server")
    curl_parser.add_argument("-X", "--verb", help="specify HTTP verb explicitly (GET and POST are implicit)")

    subparser.add_parser('help', help='show this help')

    # custom help message
    parser._positionals.title = "commands"

    args = parser.parse_args()

    # create console handler with coloured output
    ch = logging.StreamHandler()
    ch.setLevel(args.verbose)
    ch.setFormatter(ColorFormatter())
    logging.basicConfig(level=args.verbose, handlers=[ ch ])

    configurator = Configurator(args)
    documenter = BpmDocumenter(args)
    validator = BpmnValidator(args)
    editor = BpmnEditor(args)
    deployer = BpmDeployer(args, configurator, validator)
    curl = Curl(args, configurator)

    try:
        if args.cmd == 'cache':
            cache(args)
        elif args.cmd == 'validate':
            validator.validate(args.input)
        elif args.cmd == 'describe':
            editor.describe(args.id, args.input)
        elif args.cmd == 'document':
            documenter.document(args.input)
        elif args.cmd == 'get':
            editor.get(args.type, args.input)
        elif args.cmd == 'set':
            editor.set_(args.id, args.target, args.value, args.input)
        elif args.cmd == 'setextension':
            editor.set_ext(args.id, args.target, args.value, args.input)
        elif args.cmd == 'setresource':
            editor.set_res(args.id, args.value, args.input)
        elif args.cmd == 'implement':
            deployer.implement(args.input)
        elif args.cmd == 'package':
            deployer.package(args.input, args.output)
        elif args.cmd == 'deploy':
            if (args.password):
                args.password = getpass()
            deployer.deploy(args.app, args.target)
        elif args.cmd == 'curl':
            curl.make_request(args.target, args)
        else:
            help(parser)
        sys.exit(0)
    except KpException as e:
        sys.exit(e.err.value)

# Do it!
if __name__ == "kpctl" or __name__ == "__main__":
    main()

