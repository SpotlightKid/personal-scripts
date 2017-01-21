#!/usr/bin/env python
# encoding=utf8
"""Convert Markdown text from inline URL link style to
reference style and vice-versa.

http://3e156c33bb09beb35fd0-19fc75fdc34cce7558ab01263b95946a.r86.cf1.rackcdn.com/formd.py

Seth Brown 02-24-12

"""

from __future__ import print_function

import re

from collections import OrderedDict


class ForMd(object):
    """Format Markdown text."""

    def __init__(self, text):
        super(ForMd, self).__init__()
        self.text = text
        self.match_links = re.compile(r'(\[[^^]*?\])\s?(\[.*?\]|\(.*?\))',
                                      re.DOTALL | re.MULTILINE)
        self.match_refs = re.compile(r'(?<=\n)\[[^^]*?\]:\s?.*')
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
        links = (i for i in self._links())
        refs = self._refs()

        for n, link in enumerate(links):
            text, ref = link
            ref_num = ''.join(("[", str(n+1), "]: "))

            if ref in refs.keys():
                url = refs.get(ref).strip()
                formd_ref = ''.join((ref_num, url))
                formd_text = ''.join((text, ref_num))
                self.data.append([formd_text, formd_ref])
            elif text in refs.keys():
                url = refs.get(text).strip()
                formd_ref = ''.join((ref_num, url))
                formd_text = ''.join((text, ref_num))
                self.data.append([formd_text, formd_ref])
            elif ref not in refs.keys():
                parse_ref = ref.strip("()")
                formd_ref = ''.join((ref_num, parse_ref))
                formd_text = ''.join((text, ref_num))
                self.data.append([formd_text, formd_ref])

    def inline_md(self):
        """Generate Markdown with inline URLs."""
        self._format()
        text_link = iter([''.join((_[0].split("][", 1)[0],
                                  "](", _[1].split(":", 1)[1].strip(), ")"))
                          for _ in self.data])
        formd_text = self.match_links.sub(lambda _: next(text_link), self.text)
        formd_md = self.match_refs.sub('', formd_text).strip()
        return formd_md

    def ref_md(self):
        """Generate Markdown with referenced URLs."""
        self._format()
        ref_nums = iter([_[0].rstrip(" :") for _ in self.data])
        formd_text = self.match_links.sub(lambda _: next(ref_nums), self.text)
        formd_refs = self.match_refs.sub('', formd_text).strip()
        references = (i[1] for i in self.data)
        formd_md = '%s\n\n\n%s' % (formd_refs, '\n'.join(references))
        return formd_md

    def flip(self):
        """Convert markdown to the opposite style of the first text link."""
        first_match = re.search(self.match_links, self.text).group(0)

        if first_match and '(' in first_match and ')' in first_match:
            formd_md = self.ref_md()
        else:
            formd_md = self.inline_md()

        return formd_md


def pythonista_main():
    import clipboard
    import console

    md = clipboard.get()
    if md:
        text = ForMd(md)
        md = text.flip()
        clipboard.set(md)
        console.clear()
        print(md)


def main():
    import sys

    try:
        with open(sys.argv[1]) as fp:
            text = ForMd(fp.read())
            print(text.flip())
    except IndexError:
        sys.exit("Usage: formd.py <markdown file>")
    except (IOError, OSError) as exc:
        sys.exit(str(exc))


if __name__ == '__main__':
    try:
        pythonista_main()
    except ImportError:
        main()
