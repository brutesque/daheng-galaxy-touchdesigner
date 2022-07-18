#!/usr/bin/python3
import td


def onValuesChanged(changes):
    for c in changes:
        # use par.eval() to get current value
        par = c.par
        prev = c.prev
        if par.name == 'Active':
            try:
                thread = me.fetch('thread')
            except td.tdError as e:
                thread = None
            active = par.eval()
            if active is True and (thread is None or not thread.is_alive()):
                print('starting thread')
                op('start_thread').run()
            elif active is False and thread is not None and thread.is_alive():
                request_queue = me.fetch('request_queue')
                if request_queue is not None:
                    print('stopping thread')
                    request_queue.put('stop')
        else:
            request_queue = me.fetch('request_queue', None)
            if request_queue is not None:
                request_queue.put({
                    par.name: par.eval(),
                })
    return
