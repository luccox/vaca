# -*- coding: utf-8 -*-


import time
import numpy
import multiprocessing
from multiprocessing.managers import SyncManager

import database
import utils


class Kami(object):
    def __init__(self, host, n_plankton=1, savepoint=100):
        print '\nLoading Kami 5.2\n'

        self.savepoint = savepoint

        self.db = database.Database()
        self.conn = database.Connector(self.db)

        self.tick = self.conn.root['conf']['tick']
        self.size = self.conn.root['conf']['size']
        self.mutation = self.conn.root['conf']['mutation']
        self.capacity = self.conn.root['conf']['capacity']

        self.nada = self.conn.root['nada']
        self.meteo = self.conn.root['meteo']
        self.wally = self.conn.root['wally']
        self.rookies = self.conn.root['rookies']

        self._create_managers(host, n_plankton)
        self._populate_plankton()


    def _create_queue_server(self, host, port, auth_key, queue_in, queue_out):

        class QueueManager(SyncManager):
            pass

        QueueManager.register('get_queue_in', callable = lambda: queue_in)
        QueueManager.register('get_queue_out', callable = lambda: queue_out)
        manager = QueueManager(address=(host, port), authkey=auth_key)
        manager.start() # This actually starts the server

        return manager


    def _create_managers(self, host, n_plankton):
        print 'Creating Queue Managers...'
        ini_port = 18881
        auth_key = 'chaetognata'
        self.qm = {}
        for p in xrange(n_plankton):
            self.qm[p] = {}
            port = ini_port + p
            self.qm[p]['q_in'] = multiprocessing.Queue()
            self.qm[p]['q_out'] = multiprocessing.Queue()
            self.qm[p]['server'] = self._create_queue_server(host, port, auth_key,
                                                             self.qm[p]['q_in'],
                                                             self.qm[p]['q_out'])
            print '\tQM - %i \tport: %i' % (p, port)


    def _populate_plankton(self):
        print 'Populating Planktons...'
        portions = utils.chunks(range(self.wally.shape[0]),
                                self.wally.shape[0]/len(self.qm.keys()))
        for p in self.qm.keys():
            r = portions.next()
            self.qm[p]['range'] = (r[0], r[-1])
            self.qm[p]['q_in'].put([self.capacity, self.mutation,r[0],
                                    self.wally[r[0]:r[-1]+1],
                                    self.meteo[:,r[0]:r[-1]+1],
                                    self.nada])
            print '\tQM - %i \trange: %i - %i' % (p, r[0], r[-1])


    def loop(self):
        t_loop = time.time()
        self.tick += 1
        #print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

        # rookies in
        #print 'rookies IN'
        for p in self.qm.keys():
            rookies = {}
            q = self.qm[p]['range']
            for r in self.rookies.keys():
                if q[0] <= r[0] <= q[1]:
                    if r not in rookies.keys():
                        rookies[r] = []
                    for rr in self.rookies[r]:
                        rookies[r].append(rr)
            self.qm[p]['q_in'].put([self.tick, rookies])
            #print '\tQM: %i --> %i rookies' % (p, len(rookies))
            #print '\t', rookies.keys()

        # rookies out
        #print 'rookies OUT'
        self.rookies = {}
        plankton = range(len(self.qm.keys()))
        while len(plankton):
            for p in plankton:
                if self.qm[p]['q_out'].qsize():
                    plankton.remove(p)
                    rookies = self.qm[p]['q_out'].get()
                    for r in rookies.keys():
                        if r not in self.rookies.keys():
                            self.rookies[r] = []
                        for rr in rookies[r]:
                            self.rookies[r].append(rr)
                    #print '\tQM: %i <-- %i new rookies' % (p, len(rookies))
                    #print '\t', rookies.keys()

        print 'Looping... %i - %.2f secs' % (self.tick, time.time()-t_loop)
        if not self.tick % self.savepoint:
            print 'CheckPoint!'
            self.checkpoint()


    def _update_request(self):
        # in
        #print 'update IN'
        for p in self.qm.keys():
            self.qm[p]['q_in'].put([])
            #print '\tQM: %i --> request update' % p

        # out
        #print 'update OUT'
        plankton = range(len(self.qm.keys()))
        while len(plankton):
            for p in plankton:
                if self.qm[p]['q_out'].qsize():
                    plankton.remove(p)
                    wally = self.qm[p]['q_out'].get()
                    r = self.qm[p]['range']
                    self.wally[r[0]:r[-1]+1] = wally
                    #print '\tQM: %i --> updated' % p


    def checkpoint(self):
        self._update_request()
        filename = '/home/luccox/GAIA/KAMI/wally/wally_%i.png' % (self.tick)
        occupation = numpy.array([len(self.wally[self.wally[i,j,:,0] != 0])
                                      for i in xrange(self.size)
                                      for j in xrange(self.size)]).reshape(self.size,self.size)
        utils.check_dir('wally')
        utils.pyplot_from_array(filename, occupation, self.capacity)
        print 'plot saved in %s' % filename

        self.conn.root['conf']['tick'] = self.tick
        self.conn.root['wally'] = self.wally
        self.conn.root['rookies'] = self.rookies
        self.conn.commit()
        print 'data saved in DB'


    def close(self, cp=False):
        if cp:
            self.checkpoint()
        self.conn.close()
        self.db.close()
        print 'Stopping Queue Managers...'
        for p in self.qm:
            self.qm[p]['server'].shutdown()
            print '\tQM: %i --> closed' % p

        print '\nclosing GAIA... bye bye\n'



