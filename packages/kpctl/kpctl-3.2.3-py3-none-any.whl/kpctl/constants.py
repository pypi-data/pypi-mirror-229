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

APP_NAME = 'KnowProcess Modeler'

XSD_BPMN = 'http://modeler.knowprocess.com/xsd/BPMN20.xsd'
XSD_BPMNDI = 'http://modeler.knowprocess.com/xsd/BPMNDI.xsd'
XSD_DC = 'http://modeler.knowprocess.com/xsd/DC.xsd'
XSD_DI = 'http://modeler.knowprocess.com/xsd/DI.xsd'
XSD_SEMANTIC = 'http://modeler.knowprocess.com/xsd/Semantic.xsd'
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
