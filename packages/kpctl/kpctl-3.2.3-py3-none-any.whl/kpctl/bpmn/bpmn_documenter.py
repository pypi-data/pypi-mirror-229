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
from cairosvg import svg2png
import logging
import lxml.etree as ET
import os
import requests
from kpctl.constants import NS

from kpctl.xml_support import write_pretty_xml

XSLT_PROC_RENDERER = 'http://modeler.knowprocess.com/xslt/bpmn2svg.xslt'

class BpmDocumenter():
    def __init__(self, options):
        self.options = options

    def document(self, input_):
        logging.info('generating documentation...')

        if input_.endswith('.bpmn'):
            self.generate_proc_images(input_)
        elif input_.endswith('.form'):
            self.generate_form_image(input_)
        else:
            for root, dirs, files in os.walk(input_):
                for file in files:
                    if file.endswith('.bpmn'):
                        self.generate_proc_images(root+'/'+file)
                    elif file.endswith('.form'):
                        self.generate_form_image(root+'/'+file)

        logging.info('...done')

    def generate_form_image(self, form_file):
        logging.warning(f'  generating image for {form_file} not yet implemented.')

    def generate_proc_image(self, bpmn_file, dom, diag_id, diag_count, cur_diag_pos, lang=None):
        logging.info(f'  generating image for {bpmn_file}')

        res = requests.get(XSLT_PROC_RENDERER)
        xslt = ET.fromstring(res.content)
        transform = ET.XSLT(xslt)
        if lang == None:
            newdom = transform(dom, diagramId=ET.XSLT.strparam(diag_id))
        else:
            newdom = transform(dom, diagramId=ET.XSLT.strparam(diag_id),
                                lang=ET.XSLT.strparam(lang))
        if diag_count == 1:
            write_pretty_xml(f'{bpmn_file}.svg', newdom)
        else:
            write_pretty_xml(f'{bpmn_file}.{cur_diag_pos}.svg', newdom)
        try:
            lang_suffix = '' if lang == None else f'.{lang}'
            if diag_count == 1:
                svg2png(bytestring=ET.tostring(newdom, encoding='unicode'), write_to=f'{bpmn_file}{lang_suffix}.png')
            else:
                svg2png(bytestring=ET.tostring(newdom, encoding='unicode'), write_to=f'{bpmn_file}{lang_suffix}.{cur_diag_pos}.png')
        except KeyError as e:
            logging.error(f'  ... unable to render { diag_id} from {bpmn_file} in {lang} translation, cause is {e} ', exc_info=True)
        except Exception as e:
            logging.error(f'  ... unable to render {diag_id} from {bpmn_file}, optional language is {lang}, cause is {e} ', exc_info=True)

    def generate_proc_images(self, bpmn_file):
        logging.info(f'  generating image for {bpmn_file}')

        dom = ET.parse(bpmn_file)
        diags = dom.findall('//bpmndi:BPMNDiagram', NS)
        for count, diag in enumerate(diags):
            logging.info(f'found diag {diag.get("id")}')
            self.generate_proc_image(bpmn_file, dom, diag.get('id'), len(diags), count+1)

            # now generate language variants
            langs = dom.findall('//i18n:translation[@xml:lang]', NS)
            langs = set(map(lambda x : x.get('{http://www.w3.org/XML/1998/namespace}lang'), langs))
            logging.idebug(f'  detected the following languages: "{langs}"')
            for l in langs:
                logging.info("    generating localised '{l}' image ...")
                self.generate_proc_image(bpmn_file, dom, diag.get('id'), len(diags), count+1, l)
