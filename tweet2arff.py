#!/usr/bin/env python3

import argparse
import json

import eca.arff

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
    parser.add_argument('file', type=argparse.FileType('r'), help='Twitter data source')
    parser.add_argument('output', type=argparse.FileType('w'), help='Output file')
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
