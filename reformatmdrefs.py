#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert Markdown text from inline URL link style to
reference style and vice-versa.

http://3e156c33bb09beb35fd0-19fc75fdc34cce7558ab01263b95946a.r86.cf1.rackcdn.com/formd.py

Seth Brown 02-24-12

"""

from __future__ import print_function, unicode_literals

import re
from io import open
from collections import OrderedDict


class ReformatMarkdownRefs(object):
    """Reformat links and references in Markdown text."""

    match_links = re.compile(r'(\[[^^]*?\])\s?(\[.*?\]|\(.*?\))',
                                  re.DOTALL | re.MULTILINE)
    match_refs = re.compile(r'(?<=\n)\[[^^]*?\]:\s?.*')

    def __init__(self, text):
        super(ReformatMarkdownRefs, self).__init__()
        self.text = text
        self.data = []

    def _links(self, ):
        """Find Markdown links."""
        for link in re.findall(self.match_links, self.text):
            # remove newline breaks from urls spanning multi-lines
            parsed_link = [s.replace('\n', '') for s in link]
            yield parsed_link

    def _refs(self):
        """Find Markdown references."""
        refs = re.findall(self.match_refs, self.text)
        return OrderedDict(i.split(":", 1) for i in sorted(refs))

    def _format(self):
        """Process text."""
        links = tuple(self._links())
        refs = self._refs()
        print(links)
        print(refs)

        for n, link in enumerate(links):
            text, ref = link
            ref_num = '[%i]: ' % (n + 1,)

            if ref in refs:
                url = refs.get(ref).strip()
                md_ref = ref_num + url
            elif text in refs:
                url = refs.get(text).strip()
                md_ref = ref_num + url
            else:
                parse_ref = ref.strip("()")
                md_ref = ref_num + parse_ref

            md_text = text + ref_num
            self.data.append([md_text, md_ref])

    def inline_md(self):
        """Generate Markdown with inline URLs."""
        self._format()
        print(self.data)
        text_link = iter([''.join((_[0].split("][", 1)[0],
                                  "](", _[1].split(":", 1)[1].strip(), ")"))
                          for _ in self.data])
        md_text = self.match_links.sub(lambda _: next(text_link), self.text)
        return self.match_refs.sub('', md_text).strip()

    def ref_md(self):
        """Generate Markdown with referenced URLs."""
        self._format()
        ref_nums = iter([_[0].rstrip(" :") for _ in self.data])
        md_text = self.match_links.sub(lambda _: next(ref_nums), self.text)
        md_refs = self.match_refs.sub('', md_text).strip()
        references = (i[1] for i in self.data)
        return '%s\n\n\n%s' % (md_refs, '\n'.join(references))

    def flip(self):
        """Convert markdown to the opposite style of the first text link."""
        first_match = re.search(self.match_links, self.text).group(0)

        if first_match and '(' in first_match and ')' in first_match:
            return self.ref_md()
        else:
            return self.inline_md()


def pythonista_main():
    import clipboard
    import console

    md = clipboard.get()
    if md:
        text = ReformatMarkdownRefs(md)
        md = text.flip()
        clipboard.set(md)
        console.clear()
        print(md)


def main():
    import sys

    try:
        if len(sys.argv) > 1:
            fp = open(sys.argv[1], encoding='utf-8')
        else:
            fp = sys.stdin

        text = ReformatMarkdownRefs(fp.read())
    except (IOError, OSError) as exc:
        sys.exit("Usage: reformatmdrefs.py <markdown file>" + '\n' + str(exc))
    else:
        print(text.flip())
    finally:
        if fp is not sys.stdin:
            fp.close()


if __name__ == '__main__':
    try:
        pythonista_main()
    except ImportError:
        try:
            main()
        except KeyboardInterrupt:
            print('')
