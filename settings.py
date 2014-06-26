#!/usr/bin/python
# encoding: utf-8
import sys
from workflow import Workflow

def main(wf):
    argv = wf.args
    wf.settings['wpm'] = argv[0]

if __name__ == u"__main__":
    WF = Workflow()
    sys.exit(WF.run(main))
