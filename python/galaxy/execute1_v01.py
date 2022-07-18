# me - this DAT
# 
# frame - the current frame
# state - True if the timeline is paused
# 
# Make sure the corresponding toggle is enabled in the Execute DAT.
# !/usr/bin/python3
import td


def onStart():
    active = me.parent().par.Active.eval()
    try:
        thread = me.fetch('thread')
    except td.tdError as e:
        thread = None

    if active is True and (thread is None or thread.is_alive() is False):
        print('starting thread')
        op('start_thread').run()
    elif active is False and thread is not None and thread.is_alive() is True:
        request_queue = me.fetch('request_queue')
        if request_queue is not None:
            print('stopping thread')
            request_queue.put('stop')
    return


def onCreate():
    return


def onExit():
    try:
        thread = me.fetch('thread')
    except td.tdError as e:
        thread = None
    if thread is not None and thread.is_alive() is True:
        request_queue = me.fetch('request_queue')
        if request_queue is not None:
            print('stopping thread')
            request_queue.put('stop')
    return


def frameStart(frame):
    try:
        result_queue = me.fetch('result_queue')
        value = result_queue.get_nowait()
        print(type(value), value, type(result_queue), result_queue)
        op('results').insertRow(value)
    except:
        # nothing new yet
        pass
    return


def onFrameEnd(frame):
    return


def onPlayStateChange(state):
    return


def onDeviceChange():
    return


def onProjectPreSave():
    return


def onProjectPostSave():
    return
