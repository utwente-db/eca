#!/usr/bin/env python3

import argparse
import json

import eca.arff

def file_type(mode):
    """Acts as an output file type for argparse. Always uses utf-8 encoding."""
    def handler(name):
        if name == '-':
            import sys
            if 'r' in mode:
                return sys.stdin
            elif 'w' in mode:
                return sys.stdout
            else:
                raise argparse.ArgumentTypeError("can't use mode '{}' for stdin/stdout".format(mode))

        try:
            return open(name, mode, encoding='utf-8')
        except OSError as e:
            raise argparse.ArgumentTypeError("can't open '{}': {}".format(name, e))

    return handler

def rows(tweets):
    """
    This Generator function takes an opened data file with one JSON object
    representing a tweet per line, and generates a row for each tweet.
    """
    for line in tweets:
        tweet = json.loads(line)
        yield {'tweet': tweet['text']}

def main():
    """
    Main program entry point.
    """
    parser = argparse.ArgumentParser(description='Tweet data to ARFF converter')
    parser.add_argument('file', type=file_type('r'), help='Twitter data source')
    parser.add_argument('output', type=file_type('w'), help='Output file')
    args = parser.parse_args()

    # attribute description
    fields = [
        eca.arff.Field('tweet', eca.arff.Text()),
        eca.arff.Field('@@class@@', eca.arff.Nominal(['a','b','c']))
    ]

    # create item generator
    items = rows(args.file)

    eca.arff.save(args.output, fields, items, name='ARFF for '+args.file.name)

if __name__ == '__main__':
    main()
