# -*- coding: utf-8 -*-


import os
import numpy
import shutil
import random
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
from collections import Counter


########################################################################

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
        http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def check_dir(d):
    dd = '/home/luccox/GAIA/KAMI/%s' % d
    if not os.path.exists(dd):
        os.makedirs(dd)


def empty_dir(d):
    dd = '/home/luccox/GAIA/KAMI/%s' % d
    for i in os.listdir(dd):
        os.remove('%s/%s' % (dd, i))


def darwinize(array):
    b = numpy.array([array[i,j,k,3:] \
        for i in xrange(array.shape[0]) \
        for j in xrange(array.shape[1]) \
        for k in xrange(array.shape[2]) \
        if array[i,j,k,0]])

    return Counter([tuple(i) for i in b])


def profile_fito(f):
    print """
    GEN  = %i               SEM = %i (%i)           LUZ  = %i (%.2f)
    MAX  = %i (%i)        NRG = %i (%.2f)       AGUA = %i (%.2f)
    META = %i (%.2f)      SEX = %i (%.2f)       POOL = %i (%.2f)
""" % (f[0], f[2], f[2]/10, f[5], f[5]/100.0,
       f[1], f[1]/10, f[3], f[3]/100.0, f[6], f[6]/100.0,
       f[8], f[8]/100.0,  f[4], f[4]/100.0, f[7], f[7]/100.0)
'''
3    0   f_gen       generacion          int             f_gen = 0.0         0
4    1   f_max       f_edad_max          int/10          f_max = 10.0        100/10
5    2   f_num       f_sem_num           int/10          f_num = 2.0         20/10
6    3   f_nrg       energy start        int/100         f_nrg = 1.0         100/100
7    4   f_sex       minimum sex nrg     int/100         f_sex = 3.0         300/100
8    5   f_luz       luz_aprov           int/100         f_luz = 0.5         50/100
9    6   f_agua      agua_aprov          int/100         f_agua = 0.5        50/100
10   7   f_pool      pool_aprov          int/100         f_pool = 0.5        50/100
11   8   f_meta      metab_req           int/100         f_meta = 3.0        300/100
'''


def pyplot_from_array(filename, matrix, val_max, val_min=0):
    fig, ax = matplotlib.pyplot.subplots()
    cmap = matplotlib.cm.jet #BuGn
    norm = matplotlib.colors.Normalize(vmin=val_min, vmax=val_max)
    cax = ax.imshow(matrix, interpolation='bilinear', norm=norm, cmap=cmap) # nearest, bilinear, bicubic
    cbar = fig.colorbar(cax)
    #ax.set_title(label)
    matplotlib.pyplot.savefig(filename)
    shutil.copyfile(filename, '/home/luccox/GAIA/KAMI/wally/web_populationmap.png')
    #matplotlib.pyplot.show()
    matplotlib.pyplot.close()
