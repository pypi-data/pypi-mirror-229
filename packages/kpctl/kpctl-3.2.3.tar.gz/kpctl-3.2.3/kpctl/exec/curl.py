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
import base64
import logging
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import urllib.request
import urllib.parse

from kpctl.exceptions import Error, KpException

class Curl():

    def __init__(self, options, configurator):
        self.options = options
        self.configurator = configurator

    def get_token(self, target):
        self.configurator.read_config(target)

        logging.info(f'attempt to login to {self.configurator.auth_url} ...')

        try:
            oauth = OAuth2Session(client=LegacyApplicationClient(client_id=self.configurator.client_id))
            token = oauth.fetch_token(token_url=self.configurator.auth_url, client_id=self.configurator.client_id,
                                      username=self.configurator.username, password=self.configurator.password)
            logging.info(f'... login succeeded')
            self.configurator.auth = 'Bearer '+token['access_token']
            return self.configurator.auth
        except Exception as e:
            print('{} Unable to login'.format(e))
            raise KpException(Error.FAILED_AUTH)

    def make_request(self, target, req_options):
        logging.info(f'making request to {req_options.url} ...')

        self.configurator.read_config(target)
        if self.configurator.auth_type == 'Basic':
            bytes_ = (self.configurator.username+':'+self.configurator.password).encode('utf-8')
            encodedBytes = str(base64.b64encode(bytes_), 'utf-8')
            self.configurator.auth = f'Basic {encodedBytes}'
        elif self.configurator.auth_type == 'openid-connect':
            self.get_token(target)
        else:
            logging.error(f'... unsupported authentication type {self.configurator.auth_type}')
            raise KpException(Error.DEPLOY_UNSUPPORTED_AUTH_TYPE)

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Authorization": self.configurator.auth,
            "X-RunAs": self.configurator.username
        }
        logging.info(f'... headers: {headers} ...')
        logging.info(f'connecting to {req_options.url}')

        if req_options.data:
            logging.debug(f'payload is: {req_options.data}')
            if req.data.find('=') != -1:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                logging.info(f'content type: {headers["Content-Type"]}')
            data = req_options.data.encode('utf-8')
            req = urllib.request.Request(req_options.url, data, headers = headers)
        else:
            req = urllib.request.Request(req_options.url, headers = headers)

        if req_options.verb:
            logging.info(f'HTTP method: {req_options.verb}')
            req.get_method = lambda: req_options.verb
        try:
            resp = urllib.request.urlopen(req)
            respData = resp.read()
            logging.info(f'SUCCESS')
            print(respData.decode('UTF-8'))
        except urllib.error.HTTPError as e:
            logging.error(f'{e.code}: {e.reason}')
