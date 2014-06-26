#!/usr/bin/python
# encoding: utf-8
import sys
from workflow import Workflow

def main(wf):
    argv = wf.args
    for arg in argv:
        try:
            wpm = int(arg)
            wf.settings['wpm'] = wpm
        except ValueError:
            if arg in ('light', 'dark'):
                wf.settings['mode'] = arg

if __name__ == "__main__":
    WF = Workflow()
    sys.exit(WF.run(main))
