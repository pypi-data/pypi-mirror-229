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
import lxml.etree as ET
import requests
from xml.dom.minidom import parseString

def local_tag(obj):
    return (obj.tag[obj.tag.find('}')+1:], obj.tag) [obj.tag.find('}')==-1]

def transform(xsl_file, xml_file, options):
    dom = ET.parse(xml_file)
    res = requests.get(xsl_file)
    xslt = ET.fromstring(res.content)
    try:
      transform = ET.XSLT(xslt)
    except Exception as e:
      logging.error(f'e', exc_info=True)
    if options.verbose < logging.INFO:
      return transform(dom, verbosity="0")
    else:
      # collect all (v=1) and let decide calling func decide what to report
      return transform(dom, verbosity="1")

def write_pretty_xml(path, dom):
    # despite many examples of parsing pretty_print=True to ET.tostring
    # my experience is that it does not work, so reluctantly duplicating parsing
    reparsed = parseString(ET.tostring(dom, encoding="utf-8"))
    pretty_print = '\n'.join([line for line in reparsed.toprettyxml(indent=' '*2).split('\n') if line.strip()])
    with open(path, 'w') as f:
        f.write(pretty_print)
