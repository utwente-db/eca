import re
from collections import namedtuple

Field = namedtuple('Field',['name','type'])

def is_empty(line):
    return not line.strip()

def is_comment(line):
    return line.startswith('%')

def is_relation(line):
    return line.lower().startswith('@relation')

def is_attribute(line):
    return line.lower().startswith('@attribute')

def is_data(line):
    return line.lower().startswith('@data')


def safe_next(it):
    try:
        return next(it)
    except StopIteration:
        return ''

def whitespace(rest):
    return rest.lstrip()

number_pattern = re.compile(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')

def numeric(rest):
    m = number_pattern.match(rest)
    if m:
        return float(m.group(0)), rest[len(m.group(0)):]
    else:
        raise ValueError('Number not parseable')

def expect(rest, string):
    result = rest.startswith(string)
    rest = rest[len(string):]
    return result, rest

identifier_escapes = {'\\':'\\', 'n':'\n', 't':'\t', 'r':'\r', '%':'%', "'":"'"}
def identifier(rest):
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
            ec = next(it)
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


class Numeric:
    def parse(self, rest):
        if rest.startswith('?'):
            return None, rest[1:]

        return numeric(rest)

    def default(self):
        return 0.0

    def __repr__(self):
        return 'Numeric'

class Text:
    def parse(self, rest):
        if rest.startswith('?'):
            return none, rest[1:]

        return identifier(rest)

    def default(self):
        return ''

    def __repr__(self):
        return 'Text'

class Nominal:
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

    def default(self):
        return self.values[0]

    def __repr__(self):
        return 'Nominal in {}'.format(self.values)

def attr_type(rest):
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
    # @attribute WS name WS type
    rest = line[len('@attribute'):].strip()
    rest = whitespace(rest)
    name, rest = identifier(rest)
    rest = whitespace(rest)
    type = attr_type(rest)
    return name, type


def parse_row(line, fields):
    line = line.strip()
    values = {}

    if not line.startswith('{'):
        print('Parsing row "{}" with {}'.format(line, fields))
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
        raise NotImplementedError('Sparse format not implemented yet.')


def load(fileish):
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

