# -*- coding: utf-8 -*-


import sys
import numpy
import random
from multiprocessing.managers import SyncManager


class Plankton(object):
    def __init__(self, host='localhost', port=10001, auth_key='chaetognata'):
        qm = self._create_queue_client(host, port, auth_key)
        self.q_in = qm.get_queue_in()
        self.q_out = qm.get_queue_out()

    def boot(self):
        init_data = self.q_in.get()
        self.capacity = init_data[0]
        self.mutation = init_data[1]
        self.initial_row = init_data[2]
        print 'initial_row --> ', self.initial_row
        self.wally = init_data[3]
        print 'wally.shape --> ', self.wally.shape
        self.meteo = init_data[4]
        print 'meteo.shape --> ', self.meteo.shape
        self.nada = init_data[5]
        print 'nada.shape --> ', self.nada.shape


    def _create_queue_client(self, host, port, auth_key):

        class QueueManager(SyncManager):
            pass

        QueueManager.register('get_queue_in')
        QueueManager.register('get_queue_out')
        manager = QueueManager(address=(host, port), authkey=auth_key)
        manager.connect() # This starts the connected client

        return manager


    def _mutate(self, p, tick):
        p[0] += 1           # p_gen +1
        p[1] = tick         # p_start
        p[2] = p[6]         # p_nrg = f_nrg
        if random.random() < self.mutation/100.0:
            p[3] += 1       # f_gen +1
            f_max = p[4]
            f_num = p[5]
            f_nrg = p[6]
            f_sex = p[7]
            f_luz = p[8]
            f_agua = p[9]
            f_pool = p[10]
            f_meta = p[11]
            var = {'f_max': f_max, 'f_num': f_num, 'f_nrg': f_nrg, 'f_sex': f_sex,
                    'f_luz': f_luz, 'f_agua': f_agua, 'f_pool': f_pool, 'f_meta': f_meta}
            r = random.choice(var.keys())
            if r in ['f_nrg', 'f_sex', 'f_meta']:
                d = random.choice([+10, -10]) # /1000
            else:
                d = random.choice([+1, -1]) # 100
            var[r] += d
            if var['f_nrg'] < 1000:
                var['f_nrg'] = 1000
            if var['f_sex'] < var['f_nrg']:
                var['f_sex'] = var['f_nrg']
            #print 'mutate - r, d', r, d
            if r in ['f_luz', 'f_agua', 'f_pool']:
                rr = random.choice([i for i in ['f_luz', 'f_agua', 'f_pool'] if i != r])
                var[rr] -= d
                #print 'mutate - rr, -d', rr, -d

            p = [p[0], p[1], p[2], p[3], var['f_max'], var['f_num'],var['f_nrg'], \
                 var['f_sex'],var['f_luz'],var['f_agua'],var['f_pool'],var['f_meta']]

        return p


    def _in_luz(self, luz, f_luz, f_meta):
        luzn = f_luz * luz
        #print '\tin luz - luzn, f_meta --> ', luzn, f_meta
        if luzn > f_meta:
            #print '\tin luz --> sobra'
            return f_meta, luz - f_meta
        else:
            #print '\tin luz --> no sobra'
            return luzn, luz - luzn


    def _in_agua(self, lluvia, f_agua, f_meta):
        aguan = f_agua * lluvia
        #print '\tin_agua - aguan, f_meta --> ', aguan, f_meta
        if aguan > f_meta:
            #print '\tin_agua --> sobra'
            return f_meta, lluvia - f_meta
        else:
            #print '\tin_agua --> no sobra'
            return aguan, lluvia - aguan


    def _in_pool(self, pool, f_pool, f_meta):
        pooln = f_pool * pool
        #print '\tin_pool - pooln, f_meta --> ', pooln, f_meta
        if pooln > f_meta:
            #print '\tin_pool --> sobra'
            return f_meta, pool - f_meta
        else:
            #print '\tin_pool --> no sobra'
            return pooln, pool - pooln


    def _metabolize(self, p_start, tick, f_max, p_nrg, p_luz, p_agua, p_pool, f_meta):
        if tick <= p_start + f_max:
            #print '\tmetab - p_start, f_max --> ', p_start, f_max
            #print '\tmetab - p_nrg --> ', p_nrg
            p_nrg += min([p_agua, p_luz, p_pool]) * random.uniform(0.95, 1)
            #print '\tmetab - p_nrg+ --> ', p_nrg
            p_nrg -= 0.2 * f_meta * random.uniform(0.95, 1)
            #print '\tmetab - p_nrg- --> ', p_nrg
        else:
            #print '\tmetab - p_nrg --> ', p_nrg
            p_nrg -= (tick - p_start + f_max) * f_meta * random.uniform(0.95, 1)
            #print '\tmetab - p_nrg- --> ', p_nrg
        return p_nrg


    def _sex(self, p_nrg, f_num, f_nrg, f_sex):
        if (p_nrg >= f_sex) and (p_nrg > f_num * f_nrg ** 2):
            #print '\tsex - p_nrg, f_sex, f_num, f_nrg --> ', p_nrg, f_sex, f_num, f_nrg
            #print '\tsex - p_nrg, f_sex, f_num * f_nrg ** 2 --> ', p_nrg, f_sex, f_num * f_nrg ** 2
            p_nrg -= f_num * f_nrg ** 2 * random.uniform(1, 1.05)
            #print '\tsex - p_nrg --> ', p_nrg
            return True, p_nrg
        else:
            return False, p_nrg


    def _free_cells(self, pos):
        size = self.wally.shape[1] # wally.shape (49, 100, 10, 12)
        x = [i for i in [pos[0]-1, pos[0], pos[0]+1] if 0 <= i <= size-1]
        y = [j for j in [pos[1]-1, pos[1], pos[1]+1] if 0 <= j <= size-1]
        d = random.choice([(i,j) for i in x for j in y if self.nada[i,j]])
        #print '\tfree_cells --> ', d
        return d


    def loop(self):
        #if self.q_in.qsize():
        try:
            command = self.q_in.get()
        except EOFError:
            sys.exit('Connection to GAIA lost')

        if len(command):
            tick, rookies = command[0], command[1]
            new_rookies = {}

            for x in xrange(self.wally.shape[0]):
                xx = x + self.initial_row
                for y in xrange(self.wally.shape[1]):
                    chunk = self.wally[x,y]

                    # insert rookies
                    if (xx,y) in rookies.keys():
                        for p in rookies[(xx,y)]:
                            if chunk[chunk[:,0]!=0,0].shape[0] < self.capacity:
                                p = self._mutate(p, tick)
                                chunk = numpy.vstack([chunk, p])

                    # metabolismo
                    if not numpy.all(chunk==0):
                        sol, lluvia, pool = self.meteo[(tick/100)%10, x, y]
                        #print '################################################'
                        #print 'Fito - meteo - sol, lluvia, pool--> ', sol, lluvia, pool
                        for p in chunk:
                            if p[0]:
                                #print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                                p_start = p[1]
                                p_nrg = p[2]/1000.0
                                f_max = p[4]/10
                                f_num = p[5]/10
                                f_nrg = p[6]/1000.0
                                f_sex = p[7]/1000.0
                                f_luz = p[8]/100.0
                                f_agua = p[9]/100.0
                                f_pool = p[10]/100.0
                                f_meta = p[11]/1000.0
                                p_luz = 0.0
                                p_agua = 0.0
                                p_pool = 0.0
                                #print 'Fito - plankton - p_start,p_nrg, f_max, f_num, f_nrg, f_sex, \
                                #           f_luz, f_agua,f_pool, f_meta, p_luz,p_agua, p_pool --> ', \
                                #           p_start,p_nrg, f_max, f_num, f_nrg, f_sex, f_luz, f_agua,f_pool, \
                                #           f_meta, p_luz,p_agua, p_pool
                                if sol:
                                    p_luz, sol = self._in_luz(sol, f_luz, f_meta)
                                    #print 'Fito - p_luz, sol --> ', p_luz, sol
                                if lluvia:
                                    p_agua, lluvia = self._in_agua(lluvia, f_agua, f_meta)
                                    #print 'Fito - p_agua, lluvia --> ', p_agua, lluvia
                                if pool:
                                    p_pool, pool = self._in_pool(pool, f_pool, f_meta)
                                    #print 'Fito - p_pool, pool --> ', p_pool, pool

                                p_nrg_post_meta = self._metabolize(p_start, tick, f_max, p_nrg, p_luz, p_agua, p_pool, f_meta)
                                #print 'Fito - p_nrg_post_meta --> ', p_nrg_post_meta
                                if p_nrg_post_meta > 0:
                                    # sex
                                    hubo_mambito, p_nrg_post_sex = self._sex(p_nrg_post_meta, f_num, f_nrg, f_sex)
                                    #print 'Fito - hubo_mambito, p_nrg_post_sex --> ', hubo_mambito, p_nrg_post_sex
                                    if hubo_mambito:
                                        for i in xrange(int(f_num)):
                                            d = self._free_cells((xx,y))
                                            if d not in new_rookies.keys():
                                                new_rookies[d] = []
                                            new_rookies[d].append(p.tolist())
                                            print '+ rookie ', d
                                        p[2] = int(p_nrg_post_sex*1000)
                                        #print 'Fito - final --> ', p[2]
                                    else:
                                        p[2] = int(p_nrg_post_meta*1000)
                                        #print 'Fito - final --> ', p[2]
                                else:
                                    p = [0,0,0,0,0,0,0,0,0,0,0,0]
                                    #print 'Fito - muerte'

                    c_nz = chunk[chunk[:,0]!=0]
                    if len(c_nz) < self.capacity:
                        chunk = numpy.vstack([c_nz, numpy.zeros((self.capacity-len(c_nz),12), float)])
                    else:
                        chunk = c_nz[:self.capacity]

                    self.wally[x,y] = chunk

            self.q_out.put(new_rookies)

        else:
            print 'updating GAIA...'
            self.q_out.put(self.wally)
