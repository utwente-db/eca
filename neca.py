#!/usr/bin/env python3
import argparse
import threading

from eca import *


def main():
    parser = argparse.ArgumentParser(description='The Neca HTTP server.')
    parser.add_argument('-t', '--trace', default=False, action='store_true', help='Trace the execution of rules.')
    args = parser.parse_args()

    import simple

    context = Context(trace=args.trace)

    # run worker
    context.start()

    with context_switch(context):
        new_event('init')
        new_event('message', {'foo': 13, 'bar': 37})


if __name__ == "__main__":
    main()
