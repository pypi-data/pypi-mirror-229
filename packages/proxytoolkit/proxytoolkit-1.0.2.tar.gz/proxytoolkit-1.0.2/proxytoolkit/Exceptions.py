# Copyright (c) 2023 BrutalCoders
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

class InavalidProxyData(Exception):
    def __init__(self):
        self.message = '\n\nInvalidProxyData: Invalid Proxy Data , This error must be due to invalid type of proxys list'

    def __str__(self):
        return self.message


class PathError(Exception):
    def __init__(self) :
        self.message = '\n\nPathError  Invalid Path'
    def __str__(self) -> str:
        return self.message
    

class NetworkError(Exception):
    def __init__(self) :
        self.message = '\n\nNetworkError:  NetWork Connection is too bad or No Connection'
    def __str__(self):
        return self.message
    

class ModuleError(Exception):
    def __init__(self):
        self.message = '\n\nModuleError: Module Not Found OR Error occured when Connecting with Moduels'
    def __str__(self) :
        return self.message
    
class RequirementsError(Exception):
    def __init__(self,) :
        self.message = '\n\n RequirementsError: System doesn\'t meet Requirements '
    def __str__(self):
        return self.message
    
    

