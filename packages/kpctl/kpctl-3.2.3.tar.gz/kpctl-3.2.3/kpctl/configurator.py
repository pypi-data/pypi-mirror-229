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
import configparser
from configparser import ConfigParser
import logging
import os
from pathlib import Path

from kpctl.exceptions import Error, KpException

class Configurator():
    CFG_DIR_DEFAULT=Path.home().joinpath('.config')
    CFG_FILE='.kpctl.conf'
    CFG_TEMPLATE='''
    # Configuration for kpctl

    [dev]
    auth_type = Basic
    username = rest-admin
    password = test
    url = http://localhost:8080

    [prod]
    auth_type = openid-connect
    auth_url = https://auth.example.com/auth/realms/realm/protocol/openid-connect/token
    username = admin
    password = secret
    client_id = client1
    client_secret = very-secret-do-not-share
    url = https://prod.example.com
    '''

    def __init__(self, options):
        self.options = options

    def read_config(self, key):
        """Read the local configuration"""

        cfg_file = self.CFG_FILE
        try:
            logging.info(f'CONFIG DIR > {os.environ["XDG_CONFIG_HOME"]}')
            cfg_file = Path.joinpath(os.environ['XDG_CONFIG_HOME'], self.CFG_FILE)
        except KeyError:
            logging.info(f'$XDG_CONFIG_HOME not set, fall back to ~/.config/')
            if not(os.path.isdir(self.CFG_DIR_DEFAULT)):
                os.mkdir(self.CFG_DIR_DEFAULT)
            cfg_file = Path.joinpath(self.CFG_DIR_DEFAULT, self.CFG_FILE)

        if cfg_file.is_file():
            logging.info(f'reading configuration [{key}]')
            config = ConfigParser()
            try:
                config.read(str(cfg_file))

                self.auth_type = config.get(key, 'auth_type')
                self.auth_url = config.get(key, 'auth_url') if 'auth_url' in config[key] else ''
                self.client_id = config.get(key, 'client_id') if 'client_id' in config[key] else ''
                self.client_secret = config.get(key, 'client_secret') if 'client_secret' in config[key] else ''
                self.username = config.get(key, 'username')
                self.password = config.get(key, 'password')
                self.url = config.get(key, 'url')
                logging.info(f'... authentication type: {self.auth_type} ...')
                logging.info(f'... credentials {self.username}:**** ...')
            except configparser.NoSectionError as e:
                logging.error(f"  ... No section named '{key}' in config file", exc_info=True)
                raise KpException(Error.DEPLOY_BAD_CONFIG)
            except configparser.NoOptionError as e:
                logging.error(f"  ... reading section named '{key}' in config file", exc_info=True)
                raise KpException(Error.DEPLOY_BAD_CONFIG)
        else:
            logging.warning(f'no config file {self.CFG_FILE} found, initialising a default...')
            file = open(cfg_file, 'w')
            file.write(self.CFG_TEMPLATE)
            file.close()
            os.chmod(cfg_file, 0o600)
            raise KpException(Error.DEPLOY_BAD_CONFIG)
