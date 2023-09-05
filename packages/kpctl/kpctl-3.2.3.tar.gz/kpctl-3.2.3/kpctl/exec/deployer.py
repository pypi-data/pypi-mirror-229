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
import glob
import logging
import lxml.etree as ET
import os
from os.path import basename
from os.path import exists
import requests
from requests.auth import HTTPBasicAuth
from zipfile import ZipFile

from kpctl.exceptions import Error, KpException
from kpctl.xml_support import local_tag, write_pretty_xml

TEMPLATE_APP_DESCRIPTOR = '''{
  "key": "%s",
  "name": "%s",
  "description": "",
  "theme": "theme-10",
  "icon": "glyphicon-plus",
  "usersAccess": null,
  "groupsAccess": null
}
'''
TEMPLATE_FORM = '''{
  "key": "%s",
  "name": "%s",
  "version": 0,
  "fields": [%s
  ],
  "outcomes": []
}
'''
TEMPLATE_FORM_FIELD = '''
    {
      "fieldType": "FormField",
      "id": "%s",
      "name": "%s",
      "type": "text",
      "value": null,
      "required": false,
      "readOnly": false,
      "overrideId": true,
      "placeholder": "",
      "layout": null
    }'''
CACHE_DIR = os.path.expanduser('~') + '/.kp'
BPMN_XSD_ROOT_PATH = CACHE_DIR + '/xsd/BPMN20.xsd'

XSD_BPMN = 'http://modeler.knowprocess.com/xsd/BPMN20.xsd'
XSD_BPMNDI = 'http://modeler.knowprocess.com/xsd/BPMNDI.xsd'
XSD_DC = 'http://modeler.knowprocess.com/xsd/DC.xsd'
XSD_DI = 'http://modeler.knowprocess.com/xsd/DI.xsd'
XSD_SEMANTIC = 'http://modeler.knowprocess.com/xsd/Semantic.xsd'
XSLT_VALIDATOR = 'http://modeler.knowprocess.com/xslt/bpmn2issues.xslt'
XSLT_EXT_VALIDATOR = 'http://modeler.knowprocess.com/xslt/bpmn2flowableissues.xslt'
XSLT_PROC_RENDERER = 'http://modeler.knowprocess.com/xslt/bpmn2svg.xslt'
XSLT_PROC_ENHANCER = 'http://modeler.knowprocess.com/xslt/bpmn2executable.xslt'

NS = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'bpsim': 'http://www.bpsim.org/schemas/1.0',
    'color': 'http://www.omg.org/spec/BPMN/non-normative/color/1.0',
    'di': 'http://www.omg.org/spec/DD/20100524/DI',
    'dc': 'http://www.omg.org/spec/DD/20100524/DC',
    'dmn': 'http://www.omg.org/spec/DMN/20180521/MODEL/',
    'dmn12': 'http://www.omg.org/spec/DMN/20180521/MODEL/',
    'feel': 'https://www.omg.org/spec/DMN/20191111/FEEL/',
    'i18n': 'http://www.omg.org/spec/BPMN/non-normative/extensions/i18n/1.0',
    'activiti': 'http://activiti.org/bpmn',
    'camunda': 'http://camunda.org/schema/1.0/bpmn',
    'drools': 'http://www.jboss.org/drools',
    'flowable': 'http://flowable.org/bpmn',
    'html': 'http://www.w3.org/1999/xhtml',
    'kp': 'http://knowprocess.com/bpmn',
    'openapi': 'https://openapis.org/omg/extension/1.0',
    'rss': 'http://purl.org/rss/2.0/',
    'triso': 'http://www.trisotech.com/2015/triso/modeling',
    'trisobpmn': 'http://www.trisotech.com/2014/triso/bpmn',
    'trisofeed': 'http://trisotech.com/feed',
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

def camel_case(s):
    return s[0:1].lower() + s[1:].replace(' ','')

class BpmDeployer():

    DEPLOYMENT_API = '/flowable-rest/app-api/app-repository/deployments'

    def __init__(self, options, configurator, validator):
        self.options = options
        self.configurator = configurator
        self.validator = validator

    def deploy(self, app, target):
        logging.info(f'deploying {app} to {target} ...')

        if not app.endswith('bar') and not app.endswith('zip'):
            logging.info(f'... cannot deploy {app}, must be .bar or .zip')
            raise KpException(Error.DEPLOY_UNSUPPORTED_APP)

        self.configurator.read_config(target)
        if self.configurator.auth_type == 'Basic':
            r = requests.post(self.get_deployment_api(self.configurator.url), data={'file':app},
                files={'file': open(app, 'rb')},
                auth = HTTPBasicAuth(self.configurator.username, self.configurator.password))
            if r.status_code <= 400:
                logging.info(f'...done, status: '+str(r.status_code))
            else:
                logging.info(f'...error: '+str(r.status_code))
                raise KpException(Error.DEPLOY_FAILED)
        else:
            logging.info(f'... unsupported authentication type {self.configurator.auth_type}')
            raise KpException(Error.DEPLOY_UNSUPPORTED_AUTH_TYPE)

    def generate_app(self, root):
        appPath = '%s/%s.app' % (root, root)
        if exists(appPath) and not(self.options.force):
            logging.warning(f"  ... app '{appPath}' already exists, --force to overwrite")
        else:
            count = 0
            for filename in glob.glob(root+"/*.app"):
                logging.info(f"  ... found '%s', not generating another app descriptor" % filename)
                count += 1

            if count == 0:
                logging.info(f'  generating app at %s ...' % root)
                file = open(appPath, 'w')
                key = root[0:1].upper() + root[1:]
                file.write(TEMPLATE_APP_DESCRIPTOR % (key, key))
                file.close()

    def generate_forms(self, bpmn_file):
        logging.info(f'  generating forms for ...'+bpmn_file)

        dom = ET.parse(bpmn_file)
        for startEvent in dom.findall('//bpmn:startEvent', NS):
            self.generate_form(bpmn_file, dom, startEvent)
        for userTask in dom.findall('//bpmn:userTask', NS):
            self.generate_form(bpmn_file, dom, userTask)

    def generate_form(self, bpmn_file, dom, bpmn_obj):
        name = bpmn_obj.get('name')
        formKey = bpmn_obj.get('{http://knowprocess.com/bpmn}formKey')
        if formKey == None:
            formKey = bpmn_obj.get('{http://flowable.org/bpmn}formKey')
        formPath = '%s/%s.form' % (bpmn_file[:bpmn_file.rfind('/')], formKey)

        if formKey == None:
            logging.warning(f"  ... found {local_tag(bpmn_obj)} '{name}', but it has no formKey")
        elif exists(formPath) and not(self.options.force):
            logging.warning(f"  ... found {local_tag(bpmn_obj)} '{name}', but form already exists with key '{formKey}' --force to overwrite")
        else:
            print("  ... generating stub form '%s'" % formKey)
            fields = ''
            data_inputs = dom.findall('//bpmn:process/bpmn:ioSpecification/bpmn:dataInput', NS) if (local_tag(bpmn_obj) == 'startEvent') else dom.findall('//*[@id="{}"]//bpmn:dataInput'.format(bpmn_obj.get('id')), NS)
            for count, data_input in enumerate(data_inputs):
                fields += TEMPLATE_FORM_FIELD % (camel_case(data_input.get('name')),
                                                data_input.get('name'))
                if (count+1 < len(data_inputs)):
                    fields += ','
            file = open(formPath, 'w')
            file.write(TEMPLATE_FORM % (formKey, formKey if name == None else name, fields))
            file.close()

    def generate_proc_executable(self, bpmn_file):
        logging.info(f'  generating executable process for %s ...' % bpmn_file)

        fileStart = int(bpmn_file.rfind('/'))+1
        implPath = '%s/%s.kp.bpmn' % (bpmn_file[:fileStart], bpmn_file[fileStart:bpmn_file.rfind('.')]) if fileStart > 0 else ('%s.kp.bpmn' % bpmn_file[:bpmn_file.rfind('.')])
        if exists(implPath):
            logging.warning(f"  ... overwriting executable process '{implPath}' ...")

        dom = ET.parse(bpmn_file)
        res = requests.get(XSLT_PROC_ENHANCER)
        xslt = ET.fromstring(res.content)
        transform = ET.XSLT(xslt)
        write_pretty_xml(implPath, transform(dom, unsupportedTasksToUserTask=ET.XSLT.strparam('false')))

    def get_deployment_api(self, target):
        logging.info(f'deploying to {target}{self.DEPLOYMENT_API}...')

        return target+self.DEPLOYMENT_API

    def implement(self, input_):
        logging.info(f'generating implementation hints...')

        if input_.endswith('.bpmn'):
            self.generate_forms(input_)
            if not input_.endswith('.kp.bpmn'):
                self.generate_proc_executable(input_)
        else:
            for root, dirs, files in os.walk(input_):
                self.generate_app(root)
                for file_ in files:
                    if file_.endswith('.bpmn'):
                        self.generate_forms(root+'/'+file_)
                        if not file_.endswith('.kp.bpmn'):
                            self.generate_proc_executable(root+'/'+file_)

        logging.info(f'...done')

    def is_executable(self, file_name):
        if (file_name.endswith('kp.bpmn')):
            dom = ET.parse(file_name)
            return dom.findall('//bpmn:process[@isExecutable="true"]', NS)
        else:
            exts_inc = tuple(['app', 'form', 'md', 'txt'])
            return file_name.endswith(exts_inc)

    # Zip the files from given directory that matches the filter
    def zipFilesInDir(self, dirName, zipFileName, filter):
        zipFileName = zipFileName if zipFileName.endswith('.zip') else zipFileName+'.zip'
        logging.info(f'packaging {zipFileName} from {dirName} ...')
        # create a ZipFile object
        with ZipFile(zipFileName, 'w') as zipObj:
            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(dirName):
                for filename in filenames:
                    if filter(filename):
                        # create complete filepath of file in directory
                        filePath = os.path.join(folderName, filename)
                        logging.info(f'  adding: {filePath}')
                        zipObj.write(filePath, basename(filePath))

    def package(self, dir_name, file_name):

        self.validator.validate(dir_name)
        self.implement(dir_name)

        if file_name == None or len(file_name) == 0:
            file_name = dir_name[:(len(dir_name)-1)] if dir_name.endswith('/') else dir_name
            logging.info(f'defaulted file_name to {file_name}')

        self.zipFilesInDir(dir_name, file_name, lambda name : self.is_executable(os.path.join(dir_name, name)))

        logging.info(f'...done')
