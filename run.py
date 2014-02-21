#!/usr/bin/python2
# -*- coding: utf-8 -*-


import sys
import time


def start_kami(delay):
    import kami
    k = kami.Kami(n_plankton=3)
    time.sleep(delay)
    while True:
        k.loop()


def start_plankton(pt):
    import plankton
    p = plankton.Plankton(host='192.168.1.111', port=pt)
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

