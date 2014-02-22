#!/usr/bin/python2
# -*- coding: utf-8 -*-


import sys
import time


def start_kami(delay):
    import kami
    k = kami.Kami('192.168.1.111', n_plankton=3)
    time.sleep(float(delay))
    while True:
        k.loop()


def start_plankton(pt):
    import plankton
    p = plankton.Plankton('192.168.1.111', int(pt))
    p.boot()
    while True:
        p.loop()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: %s {kami <delay>| plankton <port>}' % sys.argv[0])
    else:
        if sys.argv[1] == 'kami':
            start_kami(sys.argv[2])

        elif sys.argv[1] == 'plankton':
            start_plankton(sys.argv[2])
        else:
            sys.exit('command not understood')

