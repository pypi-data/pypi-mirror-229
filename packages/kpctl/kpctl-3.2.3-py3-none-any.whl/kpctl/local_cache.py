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
import logging
import os
from os.path import exists
from os import mkdir
import requests

from kpctl.constants import XSD_BPMN, XSD_BPMNDI, XSD_DC, XSD_DI, XSD_SEMANTIC

CACHE_DIR = os.path.expanduser('~') + '/.kp'

def cache(options):
    logging.info('caching external resources...')

    if not(exists(CACHE_DIR)):
        mkdir(CACHE_DIR, 0o755)
        if not(exists(CACHE_DIR + '/xsd')):
            mkdir(CACHE_DIR + '/xsd', 0o755)

    cache_file(XSD_BPMN, CACHE_DIR + '/xsd/BPMN20.xsd', options)
    cache_file(XSD_BPMNDI, CACHE_DIR + '/xsd/BPMNDI.xsd', options)
    cache_file(XSD_DC, CACHE_DIR + '/xsd/DC.xsd', options)
    cache_file(XSD_DI, CACHE_DIR + '/xsd/DI.xsd', options)
    cache_file(XSD_SEMANTIC, CACHE_DIR + '/xsd/Semantic.xsd', options)

    logging.info('... done.')

def cache_file(url, file_path, options):
    if not(exists(file_path)):
        logging.info(f'...{file_path}...')

        file = open(file_path, 'wb')
        file.write(requests.get(url).content)
        file.close()
