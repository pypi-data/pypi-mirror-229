"""General installation information"""


class _bm:
    from os import listdir


author:   str = str('feetbots')
"""The creator of tooltils"""
version:  str = str('1.4.4-1')
"""Current installation version"""
released: str = str('7/9/2023')
"""Release date of current version"""
lines:    int = int(0)
"""How many lines of code in this version"""
license:  str = str("""
MIT License

Copyright © 2023 feetbots

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
"""The content of the currently used license"""

files: list = _bm.listdir('./') + ['tooltils/' + i for i in _bm.listdir('./tooltils')] + \
              ['tooltils/sys/' + i for i in _bm.listdir('./tooltils/sys')]

for i in files:
    if '.DS_Store' in i or '__pycache__' in i:
        files.remove(i)
    else:
        try:
            with open(i) as _f:
                lines += len(_f.readlines())
        except (IsADirectoryError, UnicodeDecodeError):
            pass

del _bm, files
