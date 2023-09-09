# MIT License

# Copyright (c) 2023 Kevin Walchko

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import subprocess
from colorama import Fore
import sys


class Command:
    def run(self, cmd):
        chunks = cmd.split(' ')
        process = subprocess.Popen(
            chunks,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.handleError(cmd, stderr.decode("utf8"))
        return stdout.decode("utf8")

    def handleError(self, cmd, err):
        if len(err) > 0:
            if err.find("Warning:") > -1:
                return
            err = err.replace("\n", "\n ")
            print(f"{Fore.RED}[stderr]--------------------")
            print(f"{Fore.CYAN}>>> {cmd}")
            print(f"{Fore.RED}----------------------------")
            print(f"{Fore.RED} {err}{Fore.RESET}")
            sys.exit(1)