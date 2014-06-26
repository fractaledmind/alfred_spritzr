#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import re
import sys
import time
import math
import plistlib
import subprocess
from workflow import Workflow, bundler

PWD = os.path.dirname(os.path.realpath(__file__))
VIEWER = bundler.utility('viewer')
VIEWER_WIDTH = 600
VIEWER_HEIGHT = 1080


##################################################
#   ORP Function                                 #
##################################################

def get_orp(chars):
    """Get Optimal Reading Position (ORP) given ``chars``.
    ORP is slightly left of center.

    :param chars: len of string object
    :type chars: ``integer``
    :returns: value of ORP
    :rytpe: ``integer``
    """
    if chars < 3:
        orp = chars
    else:
        percentage = 0.35
        orp = int(math.ceil(chars * percentage))
        if orp > 5:
            orp = 5
    return orp


##################################################
#   Spritzr Class                                 #
##################################################

class Spritzr(object):
    """Speed-reader"""

    def __init__(self, text, wpm, workflow):
        """Initialization

        :param text: string object for spritzing
        :type text: ``unicode`` or ``str``
        :param wpm: [optional] words per minute
        :type wpm: ``integer``
        :param workflow: the Workflow() object
        :type workflow: ``object``
        """
        self.wf = workflow
        self.spw = (60.0 / wpm)             # seconds per word
        self.mspw = int(self.spw * 1000)    # milliseconds per word
        # get array of ``text`` tokens
        self.tokens = self.tokenize(text)
        ## get len of largest word
        self.max_len = self.find_max()
        ## get width of window in pixels
        self.pixel_width = ((self.max_len + 4) * 36)
        

    def read(self):
        """Main public API method.
        Generate Spritzr interface and pass words through.
        """
        # set width of viewer window to ``self.pixel_width``
        self.prepare_viewer()
        
        # prepare the display
        start_word = self.spritz_word('[START]')
        self.display_word(start_word)

        # open the viewer
        cmd = ['open', VIEWER, '--args', self.wf.datafile('spritzr.html')]
        subprocess.check_output(cmd)
        # ensure viewer window is frontmost
        self.focus_viewer()
        time.sleep(1.5)

        # iterate and display all words
        last_displayed = ''
        for word in self.tokens:
            if word == "<pause>":
                # display last word to create <pause> effect
                self.display_word(last_displayed)
                time.sleep(self.spw)
            else:
                html_word = self.spritz_word(word)
                last_displayed = html_word
                self.display_word(html_word)
                time.sleep(self.spw)

        # clean ``spritzr.html`` file for next use
        start_word = self.spritz_word('[END]')
        self.display_word(start_word)
        
        self.reset_viewer()


    ##################################################
    #   Initialization Functions                     #
    ##################################################

    def tokenize(self, text):
        """Clean up input text and insert appropriate pauses.

        :param text: string object for spritzing
        :type text: ``unicode`` or ``str``
        :returns: words in ``text`` with pauses after stops
        :rytpe: ``list``
        """
        # pause after half- and full-stops
        reading = re.sub(r"(\.|,|!|\?|-|;)", "\\1 <pause> ", text)
        # double pause for new paragraph
        reading = re.sub(r"\n+", " <pause> <pause> ", text)
        reading = reading.strip()
        return reading.split()

    def find_max(self):
        """Find longest word in ``words``.

        :returns: number of characters in the longest word
        :rytpe: ``integer``
        """
        words = [word for word in self.tokens if word != '<pause>']
        words = sorted(words, key=len, reverse=True)
        return len(words[0])

    ##################################################
    #   `viewer.app` Functions                       #
    ##################################################

    def prepare_viewer(self):
        """Prepare the width of the HTML Viewer.

        :returns: True if rewrite of ``viewer.app` plist successful
        :rytpe: ``Boolean``
        """
        # get ``viewer.app`` Plist info
        viewer_plist = os.path.join(VIEWER, 'Contents/document.wflow')
        viewer_info = plistlib.readPlist(viewer_plist)
        params = viewer_info['actions'][0]['action']['ActionParameters']
        # set width of ``viewer.app`` window to ``pixel_width``
        params['targetSizeX'] = self.pixel_width
        params['targetSizeY'] = 150
        plistlib.writePlist(viewer_info, viewer_plist)
        return True

    def focus_viewer(self):
        """Ensure ``viewer.app`` is frontmost window
        """
        as_scpt = """try
            tell application "System Events" to set frontmost of process "Application Stub" to true
        end try
        """
        proc = subprocess.Popen(['osascript', '-e', as_scpt],
                                stdout=subprocess.PIPE)
        proc.communicate()

    def reset_viewer(self):
        """Prepare the width of the HTML Viewer.

        :returns: True if rewrite of ``viewer.app` plist successful
        :rytpe: ``Boolean``
        """
        # get ``viewer.app`` Plist info
        viewer_plist = os.path.join(VIEWER, 'Contents/document.wflow')
        viewer_info = plistlib.readPlist(viewer_plist)
        params = viewer_info['actions'][0]['action']['ActionParameters']
        # set width of ``viewer.app`` window to ``pixel_width``
        params['targetSizeX'] = VIEWER_WIDTH
        params['targetSizeY'] = VIEWER_HEIGHT
        plistlib.writePlist(viewer_info, viewer_plist)
        return True

    ##################################################
    #   Spritzing Functions                          #
    ##################################################

    def spritz_word(self, word):
        """Pretty print ``word`` with spritzr color formatting

        :param word: the word to be HTML encoded
        :type word: ``unicode``
        :returns: the HTML encoded text
        :rytpe: ``str``
        """
        color_left = "<font color='red'>"
        color_right = "</font>"

        (orp, prefix, postfix) = self.calculate_spaces(word)
        # change for Python list indexing
        orp_i = orp - 1
        # wrap ORP char in HTML font code
        chars = list(word)
        chars.insert(orp_i, color_left)
        chars.insert((orp_i + 2), color_right)
        colored_word = ''.join(chars)
        # prepare appropriate buffer spaces
        pre_buffer = ('&nbsp;' * prefix)
        post_buffer = ('&nbsp;' * postfix)

        print_str = pre_buffer + colored_word + post_buffer
        return print_str.encode('ascii', 'xmlcharrefreplace')

    def display_word(self, word):
        """Use template HTML to write ``word`` to spritzr.html file for display.

        :param word: the word to be HTML encoded
        :type word: ``unicode``
        :returns: the text of the template HTML
        :rytpe: ``unicode``
        """
        html_spaces = ('&nbsp;' * (get_orp(self.max_len) + 1))

        try:
            mode = self.wf.settings['mode']
        except KeyError:
            mode = 'light'
        template_path = os.path.join(PWD, '{}_template.html'.format(mode))

        with open(template_path, 'r') as file_obj:
            template = self.wf.decode(file_obj.read())
            file_obj.close()

        new_html = template.format(text=word,
                                    width=(self.pixel_width + 30),
                                    spaces=html_spaces,
                                    ms=self.mspw)
        with open(self.wf.datafile('spritzr.html'), 'w') as file_obj:
            file_obj.write(new_html)
            file_obj.close()
        return True

    def calculate_spaces(self, word):
        """Determine buffer spaces for ``word``.

        :param word: string object for calculation
        :type word: ``unicode``
        :returns: word's ORP, number of prefix spaces, and number of post spaces
        :rytpe: ``tuple`` of ``integers``
        """
        # get ORPs
        max_orp = get_orp(self.max_len)
        orp = get_orp(len(word))
        # calculate buffer spaces
        prefix_space = ((max_orp - orp) + 2)
        postfix_space = ((self.max_len - len(word) - prefix_space) + 2)

        return (orp, prefix_space, postfix_space)


##################################################
#   Main Function                                #
##################################################

def main(wf):
    """Parse command line args and spritz text.

    :param wf: the Workflow() object
    :type wf: ``object``
    """
    #article = "Thïs is á ûnicode test. Nothing more, nothing less. Absolutely."
    #Spritzr(article, 250, wf).read()

    args = wf.args

    try:
        wpm = int(wf.settings['wpm'])
    except KeyError:
        wpm = 300

    if len(args):
        if os.path.exists(args[0]):
            with open(args[0], 'r') as file_obj:
                article = wf.decode(file_obj.read())
                file_obj.close()
            Spritzr(article, wpm, wf).read()
        else:
            Spritzr(args[0], wpm, wf).read()

    

if __name__ == "__main__":
    WF = Workflow()
    sys.exit(WF.run(main))
