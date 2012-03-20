# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import sys
import threading


class SyncronousWorker():
    def __init__(self,  task):
        self._type = SYNCHRONOUS_WORKER
        self._task = task
    
    @property 
    def type(self):
        return self._type
        
    def run(self):
        self._task.status = STATUS_PROGRESS
        
        self._task.status = STATUS_DONE
        pass
    

class ASyncronousWorker(threading.Thread):
    def __init__(self,  task):
        threading.Thread.__init__(self)
        self._type = ASYNCHRONOUS_WORKER
        self._task = task
    
    @property 
    def type(self):
        return self._type
    
    def run(self):
        self._task.status = STATUS_PROGRESS
        
        self._task.status = STATUS_DONE
        pass
    
