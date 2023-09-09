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
from colorama import Fore
from pathlib import Path
import os
from .cmd import Command


class Git(Command):
    def config(self, name, email=None):
        """
        Sets up global config for user and email. If no email is
        given, then it defaults to {name}@users.noreply.github.com

        git config --global user.name {name}
        git config --global user.email {email}
        """
        if email is None:
            email = name + "@users.noreply.github.com"
        out = self.run(f"git config --global user.name {name}")
        out = self.run(f"git config --global user.email {email}")

    def pull(self):
        out = self.run("git pull")
        return out

    # def outdated(self):
    #     out = self.run("")


def pull(folder=None):
    # given a folder, it will change into each subfolder
    # and do a "git pull"
    if folder is None:
        folder = "."

    cmd = Git()
    dirname = Path(folder).expanduser().absolute()
    for d in [f for f in dirname.iterdir() if f.is_dir()]:
        os.chdir(str(d))
        git_repo = Path(".git").exists()
        if git_repo:
            print(f"{Fore.CYAN}=======================")
            print(f"{d.stem}")
            out = cmd.run("git config --get remote.origin.url")
            out = out.replace("\n","").split(":")[1]
            print(f"{out}")
            print(f"======================={Fore.RESET}")

            out = cmd.pull()
            # out = out.replace("\n", "\n ")
            if out.find("Already up to date.") > -1:
                print(f"{Fore.GREEN}{out}{Fore.RESET}")
            else:
                print(f"{out}")

            out = cmd.run("git status")
            if out.find("Untracked") > -1:
                print(f"{Fore.YELLOW}{out}{Fore.RESET}")
        os.chdir("..")

# pull("~/github")

def config():
    pass

def update():
    pass