#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import re
import os
import sys
import unicodedata

def decode(text, encoding='utf-8', normalization='NFC'):
    """Return ``text`` as normalised unicode.

    :param text: string
    :type text: encoded or Unicode string. If ``text`` is already a
        Unicode string, it will only be normalised.
    :param encoding: The text encoding to use to decode ``text`` to
        Unicode.
    :type encoding: ``unicode`` or ``None``
    :param normalization: The nomalisation form to apply to ``text``.
    :type normalization: ``unicode`` or ``None``
    :returns: decoded and normalised ``unicode``
    """
    if isinstance(text, basestring):
        if not isinstance(text, unicode):
            text = unicode(text, encoding)
        return unicodedata.normalize(normalization, text)


def splice(text):
    """Splice text into tuple of paragraphs.

    :param text: string object for splicing
    :type text: ``unicode`` or ``str``
    :returns: paragraphs in ``text``
    :rytpe: ``list``
    """
    # double pause for new paragraph
    reading = re.sub(r"\n+|\r+", "<paragraph>", text)
    reading = reading.strip()
    reading = [para.strip() for para in reading.split("<paragraph>")
                if len(para.strip()) > 0]
    return reading


def main():
    """Parse command line args and splice text.
    """
    #args = [decode(arg) for arg in sys.argv[1:]]
    args = ['/Users/smargheim/Documents/Evernote_Markdown_Notes/Speech Act Theory.md']
    if len(args):
        if os.path.exists(args[0]):
            with open(args[0], 'r') as file_obj:
                article = decode(file_obj.read())
                file_obj.close()
            res = splice(article)
            words = sorted(res, key=len, reverse=True)
            print(words[0].encode('utf-8'))
        else:
            pass

if __name__ == '__main__':
    main()