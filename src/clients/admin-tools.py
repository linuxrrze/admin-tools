#!/usr/bin/python3
from yast import import_module
import_module('UI')
from yast import *
from subprocess import Popen

def choose_module():
    header = Header('Name')
    items = [Item(Id('aduc'), 'Active Directory Users and Computers'),
             Item(Id('adsi'), 'ADSI Edit'),
             Item(Id('dns-manager'), 'DNS'),
             Item(Id('gpmc'), 'Group Policy Management'),
    ]
    UI.OpenDialog(Opt('mainDialog'), Table(Id('tools'), Opt('notify'), header, items))
    UI.SetApplicationTitle('Administrative Tools')

    UI.WaitForEvent()
    module = UI.QueryWidget('tools', 'Value')
    UI.CloseDialog()

    return module

def run(module):
    Popen(['y2base', module, 'ncurses']).wait()

if __name__ == "__main__":
    module = choose_module()
    run(module)
