#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe archivist
# https://github.com/rmed/zoe-archivist
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import re
import sys

parser = argparse.ArgumentParser()

parser.add_argument('--mail-subject', dest='subject')
parser.add_argument('--msg-sender-uniqueid', dest='sender')
parser.add_argument('--text/plain', dest='text')

if __name__ == '__main__':
    args, unknown = parser.parse_known_args()

    # Read mail text
    with open(args.text, "r") as f:
        body = f.read()

    section_re = re.search("section:(.*)", body, re.IGNORECASE)
    section = section_re.group(1).strip() if section_re else ""

    idc_re = re.search("id:(.*)", body, re.IGNORECASE)
    idc = idc_re.group(1).strip() if idc_re else ""

    title_re = re.search("title:(.*)", body, re.IGNORECASE)
    title = title_re.group(1).strip() if title_re else ""

    desc_re = re.search("description:(.*)", body, re.IGNORECASE)
    desc = desc_re.group(1).strip() if desc_re else ""

    tags_re = re.search("tags:(.*)", body, re.IGNORECASE)
    tags = tags_re.group(1).strip() if tags_re else ""

    # Content should end with '/content' string to prevent conflicts with
    # mail signatures
    content_re = re.search("content:(.*)/content", body,
        re.IGNORECASE | re.DOTALL)
    # content = content_re.group(1).strip() if content_re else ""
    content = ""
    if content_re:
        # 'escape' newline
        content = content_re.group(1).replace('\n', '_NL_')

    if args.subject == "Archivist new":
        # Create new card
        print(
            "message dst=archivist&tag=add-card&section=%s&title=%s&desc=%s&content=%s&tags=%s&sender=%s" % (
            section, title, desc, content, tags, args.sender))

    elif args.subject == ("Archivist edit"):
        # Edit existing card
        # Only modifies specified values
        msg = "message dst=archivist&tag=edit-card&section=%s&idc=%s&sender=%s" % (
            section, idc, args.sender)

        if title:
            msg += "&title=" + title

        if desc:
            msg += "&desc=" + desc

        if tags:
            msg += "&tags=" + tags

        if content:
            msg += "&content=" + content

        print(msg)
