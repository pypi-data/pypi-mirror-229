#****************************************************************************
#* extract_cpp_embedded_dsl.py
#*
#* Copyright 2022 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
from typing import List

#
#
#  VSC_DATACLASSES(TestSuite_testname, (MyClass), R"(
#    @vdc.randclass
#    class MyC(object):
#      a : vdc.rand_uint32_t
#  )")
#
#

class DSLContent(object):
    def __init__(self,
            )
    pass

class ExtractCppEmbeddedDSL(object):

    def __init__(self, 
            file_or_fp,
            name=None,
            macro_name="VSC_DATACLASSES"):
        self._macro_name = macro_name
        if hasattr(file_or_fp, "read"):
            # This is a stream-like object
            self._fp = file_or_fp
            if name is None:
                self.name = self._fp.name()
        else:
            self._fp = open(file_or_fp, "r")
            self.name = file_or_fp
        
        self._lineno = 0
        self._unget_ch = None
        self._last_ch = None
        self._buffer = ""
        self._buffer_i = 0

    def extract(self) -> List[DSLContent]:
        match_i = 0

        while self.find_macro():
            ch = self.getch()
            print("post-match char: %s" % ch)
            
        self._fp.close()

    def find_macro(self):

        while True:
            line = self._fp.readline()

            if line is None:
                break
            
            idx = line.find(self._macro_name)
            
            if idx >= 0:
                self._buffer = line
                self._buffer_i = len(self._macro_name)
                return True
        
        return False

    def getch(self):
        if self._buffer is None:
            return None

        if self._buffer_i >= len(self._buffer):
            try:
                self._buffer = self._fp.readline()
                self._lineno += 1
            except Exception:
                self._buffer = None
                return None
            
            if self._buffer is None:
                return None

        ret = self._buffer[self._buffer_i]
        self._buffer_i += 1
        return ret
    
    def ungetch(self, ch):
        if self._buffer is None:
            self._buffer = ch
        elif self._buffer_i > 0:
            self._buffer_i -= 1
            self._buffer[self._buffer_i] = ch
        else:
            self._buffer.insert(0, ch)

