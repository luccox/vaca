#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import time

def main(build):

    if build:
        import builder
        b = builder.Builder(100)

    import kami
    k = kami.Kami()

    while True:
        k.loop()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: %s {build | start}' % sys.argv[0])
    else:
        if sys.argv[1] == 'build':
            main(True)
        elif sys.argv[1] == 'start':
            main(False)
        else:
            sys.exit('command not understood')

