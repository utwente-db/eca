"""
ARFF format loading and saving module.

This module implements the book version [1] of the ARFF format. This means there
is no support for instance weights.

Known limitations:
  - This implementation does not parse dates

[1]: http://weka.wikispaces.com/ARFF+%28book+version%29
"""

import re
from collections import namedtuple

Field = namedtuple('Field',['name','type'])

__all__ = ['load', 'save', 'Field', 'Numeric', 'Text', 'Nominal']


#
# Line type functions
#

def is_empty(line):
    return not line.strip()

def is_comment(line):
    return line.startswith('%')

def format_comment(line):
    return '% '+line

def is_relation(line):
    return line.lower().startswith('@relation')

def format_relation(name):
    return '@relation ' + format_identifier(name) + '\n'

def is_attribute(line):
    return line.lower().startswith('@attribute')

def format_attribute(field):
    return '@attribute ' + format_identifier(field.name) + ' ' + str(field.type) + '\n'

def format_attributes(fields):
    result = []
    for field in fields:
        result.append(format_attribute(field))
    return ''.join(result)

def is_data(line):
    return line.lower().startswith('@data')

def format_data():
    return '@data\n'

def format_row(row, fields, sparse=False):
    """Formats a data row based on the given fields."""
    if sparse:
        result = []
        for i in range(len(fields)):
            field = fields[i]
            val = row.get(field.name)
            if val != field.type.default():
                result.append(format_numeric(i) + ' ' + field.type.format(val))
        return '{' + ','.join(result) + '}\n'
    else:
        result = []
        for field in fields:
            result.append(field.type.format(row.get(field.name)))
        return ','.join(result)+'\n'


def safe_next(it):
    """Returns the next character from the iterator or ''."""
    try:
        return next(it)
    except StopIteration:
        return ''


def whitespace(rest):
    """Parses whitespace at the beginning of the input."""
    return rest.lstrip()


number_pattern = re.compile(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')

def numeric(rest):
    """Parses a number at the beginning of the input."""
    m = number_pattern.match(rest)
    if m:
        rest = rest[len(m.group(0)):]
        try:
            number = int(m.group(0))
        except ValueError:
            number = float(m.group(0))
        return number, rest
    else:
        raise ValueError('Number not parsable')

def format_numeric(number):
    """Outputs a number."""
    return str(number)

def expect(rest, string):
    """Expects to see the string at the start of the input."""
    result = rest.startswith(string)
    if result:
        return result, rest[len(string):]
    else:
        return False, rest


identifier_escapes = {
    '\\': '\\',
    'n' : '\n',
    't' : '\t',
    'r' : '\r',
    '%' : '%',
    "'" : "'"
}
def identifier(rest):
    """Parses an optionally quoted identifier at the start of the input."""
    name = ''

    it = iter(rest)
    c = safe_next(it)

    # non-quoted
    if c != "'":
        while c and c not in [' ', '\t', ',']:
            name += c
            c = safe_next(it)
        return name, c + ''.join(it)

    # quoted

    # discard the opening quote by fetching next character
    c = safe_next(it)
    while c:
        if c == '\\':
            ec = safe_next(it)
            if not ec:
                raise ValueError('Input end during escape.')
            try:
                name += identifier_escapes[ec]
            except KeyError:
                name += '\\' + ec
        elif c == "'":
            break
        else:
            name += c
        c = safe_next(it)
    return name, ''.join(it)

def format_identifier(name):
    """Formats an identifier."""
    reverse_escapes = { c:ec for (ec,c) in identifier_escapes.items()}
    if any(x in name for x in [' ',','] + list(reverse_escapes.keys())):
        escaped = ''
        for c in name:
            if c in reverse_escapes:
                escaped += '\\' + reverse_escapes[c]
            else:
                escaped += c
        return "'"+escaped+"'"

    return name

class Numeric:
    """Numeric field type."""
    def parse(self, rest):
        if rest.startswith('?'):
            return None, rest[1:]

        return numeric(rest)

    def format(self, number):
        if number is None:
            return '?'
        else:
            return format_numeric(number)

    def default(self):
        return 0

    def __repr__(self):
        return 'Numeric'

    def __str__(self):
        return 'numeric'


class Text:
    """Text field type."""
    def parse(self, rest):
        if rest.startswith('?'):
            return None, rest[1:]

        return identifier(rest)

    def format(self, name):
        if name is None:
            return '?'
        else:
            return format_identifier(name)

    def default(self):
        return ''

    def __repr__(self):
        return 'Text'

    def __str__(self):
        return 'string'


class Nominal:
    """Nominal field type."""
    def __init__(self, names):
        self.values = names

    def parse(self, rest):
        if rest.startswith('?'):
            return None, rest[1:]

        name, rest = identifier(rest)
        if name in self.values:
            return name, rest
        else:
            raise ValueError('Unknown nominal constant "{}" for {}.'.format(name, self.values))

    def format(self, name):
        if name is None:
            return '?'
        else:
            if name not in self.values:
                raise ValueError('Unknown nominal constant "{}" for {}.'.format(name, self.values))
            return format_identifier(name)

    def default(self):
        return self.values[0]

    def __repr__(self):
        return 'Nominal in {}'.format(self.values)

    def __str__(self):
        return '{' + ', '.join(format_identifier(name) for name in self.values) + '}'


def attr_type(rest):
    """Parses a field type. Uses the whole rest."""
    if rest.lower() in ['numeric', 'integer', 'real']:
        return Numeric()
    elif rest.lower() in ['string']:
        return Text()
    elif rest.lower().startswith('date'):
        raise NotImplementedError('date parsing is not implemented.')
    elif rest.startswith('{') and rest.endswith('}'):
        names = []
        rest = rest[1:-1]
        while rest:
            rest = whitespace(rest)
            name, rest = identifier(rest)
            names.append(name)
            rest = whitespace(rest)
            seen, rest = expect(rest, ',')
            if not seen:
                break
        return Nominal(names)
    else:
        raise ValueError('Unknown attribute type "{}"'.format(rest))


def parse_attribute(line):
    """Parses an attribute line."""
    # @attribute WS name WS type
    rest = line[len('@attribute'):].strip()
    rest = whitespace(rest)
    name, rest = identifier(rest)
    rest = whitespace(rest)
    type = attr_type(rest)
    return name, type


def parse_row(line, fields):
    """Parses a row. Row can be normal or sparse."""
    line = line.strip()
    values = {}

    if not line.startswith('{'):
        rest = line
        first = True
        for field in fields:
            if not first:
                rest = whitespace(rest)
                seen, rest = expect(rest, ',')
            first = False
            rest = whitespace(rest)
            value, rest = field.type.parse(rest)
            values[field.name] =  value
        return values
    else:
        todo = set(range(len(fields)))
        rest = line[1:-1].strip()
        first = True
        while rest:
            if not first:
                rest = whitespace(rest)
                seen, rest = expect(rest, ',')
                if not seen:
                    break
            first = False
            rest = whitespace(rest)
            index, rest = numeric(rest)
            field = fields[index]
            rest = whitespace(rest)
            value, rest = field.type.parse(rest)
            todo.remove(index)
            values[field.name] = value
        for field in (fields[i] for i in todo):
            values[field.name] = field.type.default()
        return values


def load(fileish):
    """
    Loads a data set from an arff formatted file-like object.

    This generator function will parse the arff format's header to determine
    data shape. Each generated item is a single expanded row.

    fileish -- a file-like object
    """
    # parse header first
    lines = iter(fileish)
    fields = []
    
    for line in lines:
        if is_empty(line) or is_comment(line):
            continue
        
        if is_relation(line):
            # No care is given for the relation name.
            continue 

        if is_attribute(line):
            name, type = parse_attribute(line)
            fields.append(Field(name, type))
            continue

        if is_data(line):
            # We are done with the header, next up is 1 row per line
            break

    # parse data lines
    for line in lines:
        if is_empty(line) or is_comment(line):
            continue
        row = parse_row(line, fields)
        yield row

def save(fileish, fields, rows, name='unnamed relation', sparse=False):
    """
    Saves an arff formatted data set to a file-like object.

    The rows parameter can be any iterable. The fields parameter must be a list
    of `Field` instances.

    fileish -- a file-like object to write to
    fields -- a list of `Field` instances
    rows -- an iterable containing one dictionary per data row
    name -- the relation name, defaults to 'unnamed relation'
    sparse -- whether the output should be in sparse format, defaults to False
    """
    fileish.write(format_relation(name))
    fileish.write('\n')
    fileish.write(format_attributes(fields))
    fileish.write('\n')
    fileish.write(format_data())
    for row in rows:
        fileish.write(format_row(row, fields, sparse))
