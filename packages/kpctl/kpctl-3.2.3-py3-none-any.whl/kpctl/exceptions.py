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
from enum import Enum, unique

@unique
class Error(Enum):
    NONE = 0
    SCHEMA_INVALID = -101
    SEMANTIC_INVALID = -102
    DEPLOYMENT_INVALID = -103
    IMPL_EXISTING_FILE = -201
    IMPL_DUPE_ID = -202
    DEPLOY_FAILED = -400
    FAILED_AUTH = -401
    DEPLOY_BAD_CONFIG = -402
    DEPLOY_UNSUPPORTED_AUTH_TYPE  = -403
    DEPLOY_UNSUPPORTED_APP  = -405

class KpException(Exception):
    def __init__(self, err):
        self.err = err
        super().__init__()
    def __str__(self):
        return f'{self.err}'
