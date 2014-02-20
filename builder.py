# -*- coding: utf-8 -*-


import time
import numpy
import matplotlib.image
from persistent.dict import PersistentDict

import database
import utils


class Builder(object):
    def __init__(self, size, mutation=0.1, capacity=10, meteo_min=0, meteo_max=10):
        self.size = size
        self.mutation = mutation
        self.capacity = capacity
        self.meteo_min = meteo_min
        self.meteo_max = meteo_max
        self.build()

    def build(self):
        t = time.time()

        utils.check_dir('db')
        utils.empty_dir('db')
        utils.check_dir('wally')
        utils.empty_dir('wally')

        db = database.Database()
        conn = database.Connector(db)

        conn.root['conf'] = PersistentDict()
        conn.root['conf']['size'] = self.size
        conn.root['conf']['tick'] = 0
        conn.root['conf']['mutation'] = self.mutation
        conn.root['conf']['capacity'] = self.capacity
        conn.root['rookies'] = {}

        # nada
        conn.root['nada'] = (matplotlib.image.imread('meteo/nada.png') == 1)

        # meteo
        conn.root['meteo'] = numpy.zeros((10, self.size, self.size, 3), dtype=numpy.float)

        for i in xrange(10):
            sol = matplotlib.image.imread('meteo/sol_%i.png' %i) * self.meteo_max
            lluvia = matplotlib.image.imread('meteo/lluvia_%i.png' %i) * self.meteo_max
            pool = matplotlib.image.imread('meteo/pool_%i.png' %i) * self.meteo_max
            for x in xrange(self.size):
                for y in xrange(self.size):
                    conn.root['meteo'][i,x,y,0] = sol[x,y]
                    conn.root['meteo'][i,x,y,1] = lluvia[x,y]
                    conn.root['meteo'][i,x,y,2] = pool[x,y]

        # wally
        conn.root['wally'] = numpy.zeros((self.size, self.size, self.capacity, 12), dtype=numpy.int32)

        p_gen = 1
        p_start = 0
        p_nrg = 1000
        f_gen = 0
        f_max = 100
        f_num = 15
        f_nrg = 1000
        f_sex = 3000
        f_luz = 50
        f_agua = 50
        f_pool = 50
        f_meta = 3000
        for pos in [(self.size/4, self.size/4), \
                    (self.size/4, 3*self.size/4), \
                    (3*self.size/4, self.size/4), \
                    (3*self.size/4, 3*self.size/4)]:
            conn.root['wally'][pos[0],pos[1]][0] = [p_gen,p_start,p_nrg,f_gen,f_max,f_num, \
                                                    f_nrg,f_sex,f_luz,f_agua,f_pool,f_meta]

        print '\nBuild completed in %f secs\n' % (time.time()-t)

        conn.close()
        db.close()

