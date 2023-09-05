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
import colorama
from colorama import Fore, Style
import logging
import lxml.etree as ET
import os

from kpctl.constants import NS
from kpctl.exceptions import Error, KpException
from kpctl.local_cache import CACHE_DIR, cache
from kpctl.xml_support import transform

BPMN_XSD_ROOT_PATH = CACHE_DIR + '/xsd/BPMN20.xsd'
XSLT_VALIDATOR = 'http://modeler.knowprocess.com/xslt/bpmn2issues.xslt'
XSLT_EXT_VALIDATOR = 'http://modeler.knowprocess.com/xslt/bpmn2flowableissues.xslt'

class BpmnValidator():
    def __init__(self, options):
        self.options = options

    def validate(self, input_):
        cache(self.options)
        logging.info('validating...')

        if input_.endswith('.bpmn'):
            self.validate_bpmn(input_)
        else:
            proc_ids = []
            for root, dirs, files in os.walk(input_):
                for file_ in files:
                    if file_.endswith('.bpmn') and not(file_.endswith('.kp.bpmn')):
                        self.validate_bpmn(root+'/'+file_)
                        dom = ET.parse(root+'/'+file_)
                        for proc in dom.findall('//bpmn:process[@isExecutable="true"]', NS):
                            proc_id = proc.attrib['id']
                            if proc_ids.count(proc_id):
                                logging.error(f'More than one file contains process with id {proc_id}')
                                raise KpException(Error.IMPL_DUPE_ID)
                            else:
                                proc_ids.append(proc_id)

        logging.info('...done')

    def validate_bpmn(self, bpmn_file):
        logging.info(f'  validating ...{bpmn_file}')
        colorama.init()

        try:
            issues = self.validate_xsd(bpmn_file)
            if issues[0:5] == 'ERROR':
                print(issues)

            issues += str(transform(XSLT_VALIDATOR, bpmn_file, self.options))
            issues += str(transform(XSLT_EXT_VALIDATOR, bpmn_file, self.options))

            issueArr = issues.split('\n')
            errs = list(filter(lambda issue: issue[0:5] == 'ERROR', issueArr))
            for err in errs:
                logging.error(err.replace('ERROR: ', ''))
            warns = list(filter(lambda issue: issue[1:5] == 'WARN', issueArr))
            for warning in warns:
                logging.warning(warning.replace('WARN: ', '').strip())
            infos = list(filter(lambda issue: issue[1:5] == 'INFO', issueArr))
            logging.debug(f'found {len(infos)} information messages')
            debugs = list(filter(lambda issue: issue[0:5] == 'DEBUG', issueArr))
            logging.debug(f'found {len(debugs)} debug messages')

            for info in infos:
                logging.info(info.replace('INFO: ', ''))
            for debug in debugs:
                logging.debug(debug.replace('DEBUG: ', ''))
            print('\n  %s %s schema valid and has %d errors, %d warnings and %d messages.'
                % (bpmn_file, ('is' if 'is schema valid' in issueArr[0] else 'is not'),
                    len(errs), len(warns), len(infos)))
            if len(errs) > 0:
                raise KpException(Error.DEPLOYMENT_INVALID)
        except ET.XMLSyntaxError as e:
            issue = "ERROR: file '%s' is not well-formed XML, individual issues follow:\n" % (bpmn_file)
            for err in e.error_log:  # pylint: disable=no-member
                issue += "ERROR: Line %s: %s\n" % (err.line, err.message)
            print(issue)
            raise KpException(Error.SCHEMA_INVALID)

    def validate_xsd(self, xml_path: str) -> bool:
        xmlschema_doc = ET.parse(BPMN_XSD_ROOT_PATH)
        xmlschema = ET.XMLSchema(xmlschema_doc)
        try:
            xml_doc = ET.parse(xml_path)
            xmlschema.assertValid(xml_doc)
            return " INFO: file '%s' is schema valid\n" % (xml_path)
        except ET.XMLSyntaxError as e:
            issue = "ERROR: file '%s' is not well-formed XML, individual issues follow:\n" % (xml_path)
            for err in e.error_log:  # pylint: disable=no-member
                issue += "ERROR: Line %s: %s\n" % (err.line, err.message)
            return issue
        except ET.DocumentInvalid as e:
            issue = "ERROR: file '%s' is not schema valid, individual issues follow:\n" % (xml_path)
            for err in e.error_log:  # pylint: disable=no-member
                issue += "ERROR: Line %s: %s\n" % (err.line, err.message)
            return issue
