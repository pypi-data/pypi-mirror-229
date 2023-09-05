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
from importlib.metadata import version
import logging
import lxml.etree as ET
import os

from kpctl.constants import APP_NAME, NS
import kpctl
from kpctl.xml_support import local_tag, write_pretty_xml

class BpmnEditor():
    def __init__(self, options):
        self.options = options

    def describe(self, id_, input_):
        if input_.endswith('.bpmn'):
            self.describe_from_file(id_, input_)
        else:
            for root, dirs, files in os.walk(input_):
                for file_ in files:
                    if file_.endswith('.bpmn'):
                        self.describe_from_file(id_, root+'/'+file_)

    def describe_from_file(self, id_, bpmn_file):
        logging.info(f'describing {id_} within {bpmn_file} ...')
        colorama.init()

        dom = ET.parse(bpmn_file)
        objs = dom.findall("//*[@id='{}']".format(id_), NS)
        for obj in objs:
            ltag = local_tag(obj)
            print('  {}{}{}:{} {}'.format(Style.BRIGHT, Fore.GREEN,
                                          ltag, Style.RESET_ALL, obj.attrib['id']))
            for key in obj.keys():
                 if key != 'id':
                     print('    {}{}:{} {}'.format(Fore.GREEN, key, Style.RESET_ALL,
                                                   obj.attrib[key].replace('\n', ' ')))

            if (ltag in ['sendTask', 'serviceTask', 'businessRuleTask']):
                for platform in ['activiti','camunda','flowable','kp']:
                    exts = obj.findall(".//{}:field".format(platform), NS)
                    if (len(exts)>0):
                        print('    {}{}{} extension:{}'.format(Style.BRIGHT, Fore.CYAN,
                                                           platform, Style.RESET_ALL))
                    for ext in exts:
                        try:
                            value = ext.attrib['expression'] if 'expression' in ext.keys() else ext.attrib['stringValue']
                            print('      {}{}:{} {}'.format(Fore.CYAN, ext.attrib['name'],
                                                            Style.RESET_ALL, value))
                        except:
                            value = 'n/a'
                            expr = ext.find("./{}:expression".format(platform), NS)
                            if expr is not None:
                                 value = expr.text
                            s = ext.find("./{}:string".format(platform), NS)
                            if expr is None and s is not None:
                                 value = s.text
                            print('      {}{}:{} {}'.format(Fore.CYAN, ext.attrib['name'],
                                                            Style.RESET_ALL, value))
                    refType = obj.find(".//{}:decisionReferenceType".format(platform), NS)
                    if refType != None:
                        print('      {}decisionReferenceType:{} {}'.format(Fore.CYAN,
                                                        Style.RESET_ALL, refType.text))

            elif (ltag == 'userTask'):
                po = obj.find('.//bpmn:formalExpression', NS)
                print('    {}potentialOwner:{} {}'.format(Fore.GREEN,
                                                          Style.RESET_ALL,
                                                          'n/a' if po is None else po.text))

            di = dom.find("//*[@bpmnElement='{}']".format(id_), NS)
            if (di is None):
                print('  no diagram interchange information is available')
            else:
                print('  {}{}{}:{} {}'.format(Style.BRIGHT, Fore.MAGENTA,
                                              local_tag(di), Style.RESET_ALL, di.get('id', 'n/a')))
                for key in di.keys():
                     if key != 'id':
                         print('    {}{}:{} {}'.format(Fore.MAGENTA, key,
                                                       Style.RESET_ALL,
                                                       di.attrib[key].replace('\n', ' ')))
                di_bounds = di.find('dc:Bounds', NS)
                if di_bounds != None:
                    print('    {}{}:{} position {},{} size {},{}'.format(
                               Fore.MAGENTA, 'bounds', Style.RESET_ALL,
                               di_bounds.get('x','n/a'), di_bounds.get('y','n/a'),
                               di_bounds.get('width','n/a'), di_bounds.get('height','n/a')))
                else:
                    print('    no bounds information')
                di_label = di.find('bpmndi:BPMNLabel', NS)
                if di_label != None:
                    print('    {}{}:{} {}'.format(Fore.MAGENTA, local_tag(di_label),
                                                  Style.RESET_ALL, di.get('id','n/a')))
                    for key in di_label.keys():
                        if key != 'id':
                            print('      {}{}:{} {}'.format(Fore.MAGENTA, key,
                                                            Style.RESET_ALL,
                                                            di_label.attrib[key]))
                    di_label_bounds = di_label.find('dc:Bounds', NS)
                    if di_label_bounds != None:
                        print('      {}{}:{} position {},{} size {},{}'.format(
                                   Fore.MAGENTA, 'bounds', Style.RESET_ALL,
                                   di_label_bounds.get('x', 'n/a'),
                                   di_label_bounds.get('y', 'n/a'),
                                   di_label_bounds.get('width', 'n/a'),
                                   di_label_bounds.get('height', 'n/a')))
                    else:
                        print('    no label bounds information')
                else:
                    print('    no label information')

    def get(self, type_, input_):
        if input_.endswith('.bpmn'):
            self.get_from_file(type_, input_)
        else:
            for root, dirs, files in os.walk(input_):
                for file_ in files:
                    if file_.endswith('.bpmn'):
                        self.get_from_file(type_, root+'/'+file_)

    def get_from_file(self, type_, bpmn_file):
        logging.info(f'finding {type_} within {bpmn_file} ...')
        colorama.init()

        dom = ET.parse(bpmn_file)
        objs = dom.findall('//{}'.format((type_, 'bpmn:'+type_) [type_.find(':')==-1]), NS)
        for obj in objs:
            print('  {}{}{}: {}'.format(Fore.GREEN, obj.attrib['id'],
                                        Style.RESET_ALL,
                                        'n/a' if obj.get('name') == None else obj.get('name')))

    def set_(self, id_, target, value, input_):
        if input_.endswith('.bpmn'):
            self.set_in_file(id_, target, value, input_)
        else:
            for root, dirs, files in os.walk(input_):
                for file_ in files:
                    if file_.endswith('.bpmn'):
                        self.set_in_file(id_, target, value, root+'/'+file_)

    def set_in_file(self, id_, target, value, bpmn_file):
        logging.info(f'setting {target} of {id_} to {value} ...')

        dom = ET.parse(bpmn_file)
        obj = dom.find("//*[@id='{}']".format(id_), NS)

        if target.find(':') > -1:
            target = '{'+NS[target[0:target.find(':')]]+'}'+target[target.find(':')+1:]
        if obj == None:
            logging.warning('  object not found')
        else:
            obj.set(target, value)
            self.write_kp_bpmn(bpmn_file, dom)

            # add any missing implementation extensions
            if target == 'implementation' and value == 'kp:http':
                self.set_ext_if_missing(id_, 'requestMethod', 'GET', bpmn_file)
                self.set_ext_if_missing(id_, 'requestUrl', 'https://knowprocess.com', bpmn_file)
                self.set_ext_if_missing(id_, 'requestHeaders', 'Content-Type:application/json', bpmn_file)
                #self.set_ext_if_missing(id_, 'requestBody', '', bpmn_file)
                self.set_ext_if_missing(id_, 'resultVariablePrefix', 'st1', bpmn_file)
                self.set_ext_if_missing(id_, 'saveRequestVariables', 'false', bpmn_file)
                self.set_ext_if_missing(id_, 'saveResponseParameters', 'true', bpmn_file)
            elif target == 'implementation' and value == 'kp:mail':
                self.set_ext_if_missing(id_, 'to', 'info@knowprocess.com', bpmn_file)
            elif target == 'implementation' and value == 'kp:dmn':
                self.set_ext_if_missing(id_, 'decisionTableReferenceKey', 'decision1', bpmn_file)
                self.set_ext_if_missing(id_, 'decisionTaskThrowErrorOnNoHits', 'false', bpmn_file)

    def set_ext_if_missing(self, id_, target, value, bpmn_file):
        dom = ET.parse(bpmn_file)
        obj = dom.find("//*[@id='{}']/bpmn:extensionElements/*[@name='{}']".format(id_, target), NS)
        if (obj is None):
            self.set_ext(id_, target, value, bpmn_file)
        else:
            logging.warning(f'  {id_} already has {target} extension, skipping set')

    def set_ext(self, id_, target, value, input_):
        if input_.endswith('.bpmn'):
            self.set_ext_in_file(id_, target, value, input_)
        else:
            for root, dirs, files in os.walk(input_):
                for file_ in files:
                    if file_.endswith('.bpmn'):
                        self.set_ext_in_file(id_, target, value, root+'/'+file_)

    def set_ext_in_file(self, id_, target, value, bpmn_file):
        logging.info(f'set extension {target} of {id_} to {value} ...')

        dom = ET.parse(bpmn_file)
        obj = dom.find("//*[@id='{}']/bpmn:extensionElements/*[@name='{}']".format(id_, target), NS)
        if (obj is None):
            exts = dom.find("//*[@id='{}']/bpmn:extensionElements".format(id_), NS)
            ext = ET.SubElement(exts, ('{%s}field' % NS['kp']))
            ext.set('name', target)
            if value.find('${')==-1:
                print('  adding new extension string {}'.format(target))
                ext.set('stringValue', value)
            else:
                print('  adding new extension expression {}'.format(target))
                ext.set('expression', value)
            exts.append(ext)
        else:
            if value.find('${')==-1:
                print('  updating existing extension string {}'.format(target))
                obj.set('stringValue', value)
            else:
                print('  updating existing extension expression {}'.format(target))
                obj.set('expression', value)
        self.write_kp_bpmn(bpmn_file, dom)

    def set_res(self, id_, value, input_):
        if input_.endswith('.bpmn'):
            self.set_res_in_file(id_, value, input_)
        else:
            for root, dirs, files in os.walk(input_):
                for file_ in files:
                    if file_.endswith('.bpmn'):
                        self.set_res_in_file(id_, value, root+'/'+file_)

    def set_res_in_file(self, id_, value, bpmn_file):
        logging.info(f'set resource of {id_} to {value} ...')

        dom = ET.parse(bpmn_file)
        obj = dom.find("//*[@id='{}']/bpmn:potentialOwner".format(id_), NS)
        if (obj is None):
            logging.info(f'  creating new potentialOwner {value} ...')
            task = dom.find("//*[@id='{}']".format(id_), NS)
            po = ET.SubElement(task, ('{%s}potentialOwner' % NS['bpmn']))
            resExpr = ET.SubElement(po, ('{%s}resourceAssignmentExpression' % NS['bpmn']))
            expr = ET.SubElement(resExpr, ('{%s}formalExpression' % NS['bpmn']))
            expr.text = value
            resExpr.append(expr)
            po.append(resExpr)
            task.append(po)
        else:
            logging.info(f'  updating existing potentialOwner to {value} ...')
            dom.find("//*[@id='{}']/bpmn:potentialOwner//bpmn:formalExpression".format(id_), NS).text = value
        self.write_kp_bpmn(bpmn_file, dom)

    def write_kp_bpmn(self, path, dom):
        dom.getroot().set('exporter', APP_NAME)
        dom.getroot().set('exporterVersion', version(__package__))
        write_pretty_xml(path, dom)
