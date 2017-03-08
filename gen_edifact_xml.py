#!/usr/bin/env python3

"""
We expect a file like d16b_html/html/trmd/invoic_c.htm

taken from

wget https://www.unece.org/fileadmin/DAM/trade/untdid/d16b/d16b_html.zip

"""

from html.parser import HTMLParser
from collections import OrderedDict

class Line:
    current_SG = None
    def __init__(self):
        self.number = None
        self.segment_group = None
        self.label = ''
        self.description = ''
        self.status = ''
        self.repeats = None
        self.XXX = None
        self.level = 0
        self.seeing_X = False

    def set_description(self, data):
        if data.startswith(', '):
            data = data[2:]
        lines = data.split('\n')
        descr = []
        for line in lines[1:]:
            line = line.strip()
            if line == '':
                break
            descr.append(line.replace('"',"'"))
        self.description = ' '.join(descr)

    def set_HREF(self, data):
        data = data.strip()
        if data == self.number:
            pass
        elif len(data) == 3 and data.isalpha() and data.isupper():
            self.XXX = data
        elif self.seeing_X:
            self.set_flags(data)
        else:
            self.set_description(data)

    def set_flags(self, data):
        stripped = data.split('\n')[0].strip()
        if stripped == '|':
            return
        while stripped[-1] in '+|':
            self.level += 1
            stripped = stripped[:-1].strip()
        full = stripped
        stripped = stripped.replace('-', '')
        parts = stripped.split()
        self.label = ' '.join(parts[:-2])
        self.status = parts[-2]
        self.repeats = parts[-1]
        self.current = self
        if '-- Segment group ' in full:
            _ = full.replace('-', '')
            parts = _.split()
            Line.current_SG = parts[2]
            self.label = 'SG{}'.format(Line.current_SG)
            self.XXX = 'GROUP'
            self.level -= 1
        self.segment_group = Line.current_SG

    def __repr__(self):
        return '{} SG={} {} level={} Number={} label={} status={} repeats={} description={}'.format(
            '  ' * self.level,
            self.segment_group, self.XXX,  self.level, self.number, self.label, self.status, self.repeats, self.description)

    def __str__(self):
        return self.__repr__()


class EdiParser(HTMLParser):
    def __init__(self):
        super(EdiParser, self).__init__()
        self.current_line = None
        self.seeing_HREF = None
        self.expecting_description = False
        self.result = OrderedDict()

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.current_line = None
        elif tag == 'a':
            if len(attrs) == 1 and len(attrs[0]) == 2:
                if attrs[0][0] == 'name':
                    data = attrs[0][1].replace('_X', '')
                    if data not in self.result:
                        self.result[data] = Line()
                        self.result[data].number = data
                    self.current_line = self.result[data]
                    self.current_line.seeing_X = attrs[0][1].endswith('_X')
                    self.seeing_HREF = False
                elif attrs[0][0] == 'href' and self.current_line:
                    self.seeing_HREF = True

    def handle_data(self, data):
        data = data.strip()
        if data:
            if self.current_line and self.seeing_HREF:
                self.current_line.set_HREF(data)

    def to_xml(self):
        tab = ' ' * 5
        result = ['<TRANSMISSION>']
        prev = None
        for line in self.result.values():
            if line.XXX in ('UNH', 'BGM', 'UNT'):
                continue
            if prev and (prev.segment_group != line.segment_group or prev.level > line.level):
                for undent in reversed(range(prev.level - line.level)):
                    result.append('{indent}</GROUP>'.format(indent=tab * (1 + line.level + undent),undent=undent))
            result.append('{indent}<{XXX} status="{status}" repeats="{repeats}" label="{label}" description="{number}: {description}">{TRAIL}'.format(
                indent=tab*(1+line.level), TRAIL='</{}>'.format(line.XXX) if line.XXX != 'GROUP' else '', **line.__dict__))
            prev = line
        for undent in reversed(range(prev.level)):
            result.append('{indent}</GROUP>'.format(indent=tab * (1 + line.level + undent),undent=undent))
        result.append('</TRANSMISSION>')
        return '\n'.join(result)


def main():
    parser = EdiParser()
    text = open('invoic_c.htm', encoding='iso8859-1').read()
    parser.feed(text)
    print(parser.to_xml())


if __name__ == '__main__':
    main()
