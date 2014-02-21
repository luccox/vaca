# -*- coding: utf-8 -*-


import time
import multiprocessing
from multiprocessing.managers import SyncManager

import database
import utils


class Kami(object):
    def __init__(self, n_plankton=1, savepoint=100):
        print '\nLoading Kami 5.1\n'

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

        self._create_managers(n_plankton)
        self._populate_plankton()


    def _create_queue_server(self, host, port, auth_key, queue_in, queue_out):

        class QueueManager(SyncManager):
            pass

        QueueManager.register('get_queue_in', callable = lambda: queue_in)
        QueueManager.register('get_queue_out', callable = lambda: queue_out)
        manager = QueueManager(address=(host, port), authkey=auth_key)
        manager.start() # This actually starts the server

        return manager


    def _create_managers(self, n_plankton):
        host = ''
        ini_port = 10001
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


    def _populate_plankton(self):
        portions = utils.chunks(range(self.wally.shape[0]),
                                self.wally.shape[0]/len(self.qm.keys()))
        for p in self.qm.keys():
            r = portions.next()
            self.qm[p]['range'] = (r[0], r[-1])
            self.qm[p]['q_in'].put([self.capacity, self.mutation,r[0],
                                    self.wally[r[0]:r[-1]],
                                    self.meteo[:,r[0]:r[-1]],
                                    self.nada])


    def loop(self):
        t_loop = time.time()
        self.tick += 1

        # rookies in
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

        # rookies out
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

        print 'Looping... %i - %.2f secs' % (self.tick, time.time()-t_loop)
        if not self.tick % self.savepoint:
            print 'CheckPoint!... %i' % self.tick
            self.checkpoint()


    def _update_request(self):
        # in
        for p in self.qm.keys():
            self.qm[p]['q_in'].put([])

        # out
        plankton = range(len(self.qm.keys()))
        while len(plankton):
            for p in plankton:
                if self.qm[p]['q_out'].qsize():
                    plankton.remove(p)
                    wally = self.qm[p]['q_out'].get()
                    r = self.qm[p]['range']
                    self.wally[r[0]:r[-1]] = wally



    def checkpoint(self):
        self._update_request()
        self.conn.root['conf']['tick'] = self.tick
        self.conn.root['wally'] = self.wally
        self.conn.root['rookies'] = self.rookies
        self.conn.commit()

    def close(self):
        self.checkpoint()
        self.conn.close()
        self.db.close()
        for c in self.qm:
            self.qm[c]['server'].shutdown()

        print '\nclosing GAIA... bye bye\n'



