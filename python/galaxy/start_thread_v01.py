#!/usr/bin/python3
import os
import sys

# TODO: send camera values to table
# TODO: GammaParam, ContrastParam, ColorCorrectionParam, AcquisitionFrameRateMode, AcquisitionFrameRate, OffsetX, OffsetY, WidthMax, Width, HeightMax, Height
# TODO: find out what UserSetSelector and UserSetSave.send_command() do
# TODO: figure out if .set_acquisition_buffer_number(n) impacts latency
# TODO: figure out what PixelFormat does. Same for LUTValueAll, UserOutputValue
# TODO: figure out if cam.export_config_file("export_config_file.txt") is useful

my_paths = [
    os.path.join(os.path.abspath('.'), 'python', 'libs')
]
for my_path in my_paths:
    if my_path not in sys.path and os.path.exists(my_path):
        sys.path.append(my_path)

import queue
import threading
import gxipy
import numpy


# this is the function that is the guts of the thread
# when this function returns, the thread will exit
# currently, it never exits
def workFunc(request_queue, result_queue):
    while True:

        # This will block until a new enty is placed on the queue
        request_value = request_queue.get()

        if request_value == 'stop':
            break
        elif request_value == 'value':
            value = get_value()
            result_queue.put(value)
    return


def get_value():
    return absTime.frame


def camera_feed(request_queue, result_queue, image_queue, camera_params):
    device_sn = camera_params['Devicesn'] or None
    device_manager = None
    device = None

    while True:
        if device_sn is not None and device is None:
            if device_manager is None:
                device_manager = gxipy.DeviceManager()
            try:
                device = device_manager.open_device_by_sn(sn=device_sn)
            except gxipy.gxiapi.NotFoundDevice:
                pass
            if device is not None:
                device.TriggerMode.set(gxipy.GxSwitchEntry.OFF)
                device.stream_on()
                if device.GainAuto.is_implemented() and device.GainAuto.is_writable():
                    device.GainAuto.set(
                        gxipy.GxAutoEntry.CONTINUOUS if camera_params['Gainauto'] else gxipy.GxAutoEntry.OFF
                    )
                if device.ExposureAuto.is_implemented() and device.ExposureAuto.is_writable():
                    device.ExposureAuto.set(
                        gxipy.GxAutoEntry.CONTINUOUS if camera_params['Exposureauto'] else gxipy.GxAutoEntry.OFF
                    )
                if device.BalanceWhiteAuto.is_implemented() and device.BalanceWhiteAuto.is_writable():
                    device.BalanceWhiteAuto.set(
                        gxipy.GxAutoEntry.CONTINUOUS if camera_params['Balancewhiteauto'] else gxipy.GxAutoEntry.OFF
                    )
                if device.Gain.is_implemented() and device.Gain.is_writable():
                    device.Gain.set(camera_params['Gain'])
                if device.ExposureTime.is_implemented() and device.ExposureTime.is_writable():
                    device.ExposureTime.set(camera_params['Exposuretime'])
                if device.BalanceRatio.is_implemented() and device.BalanceRatio.is_writable():
                    device.BalanceRatioSelector.set(0)
                    device.BalanceRatio.set(camera_params['Balanceratiox'])
                    device.BalanceRatioSelector.set(1)
                    device.BalanceRatio.set(camera_params['Balanceratioy'])
                    device.BalanceRatioSelector.set(2)
                    device.BalanceRatio.set(camera_params['Balanceratioz'])

        if request_queue.qsize() > 0:
            # This will block until a new enty is placed on the queue
            request_value = request_queue.get()

            if request_value == 'stop':
                break
            elif request_value == 'value':
                value = get_value()
                result_queue.put(value)
            elif type(request_value) is dict:
                for key, value in request_value.items():

                    if key == 'Exposuretime' and device.ExposureTime.is_implemented() and device.ExposureTime.is_writable():
                        if device is not None:
                            device.ExposureTime.set(value)

                    elif key == 'Gain' and device.Gain.is_implemented() and device.Gain.is_writable():
                        if device is not None:
                            device.Gain.set(value)

                    elif key == 'Exposureauto' and device.ExposureAuto.is_implemented() and device.ExposureAuto.is_writable():
                        if device is not None:
                            device.ExposureAuto.set(
                                gxipy.GxAutoEntry.CONTINUOUS if value else gxipy.GxAutoEntry.OFF
                            )

                    elif key == 'Gainauto' and device.GainAuto.is_implemented() and device.GainAuto.is_writable():
                        if device is not None:
                            device.GainAuto.set(
                                gxipy.GxAutoEntry.CONTINUOUS if value else gxipy.GxAutoEntry.OFF
                            )

                    elif key == 'Balancewhiteauto' and device.BalanceWhiteAuto.is_implemented() and device.BalanceWhiteAuto.is_writable():
                        if device is not None:
                            device.BalanceWhiteAuto.set(
                                gxipy.GxAutoEntry.CONTINUOUS if value else gxipy.GxAutoEntry.OFF
                            )

                    elif key == 'Balanceratiox' and device.BalanceRatio.is_implemented() and device.BalanceRatio.is_writable():
                        if device is not None:
                            device.BalanceRatioSelector.set(0)
                            device.BalanceRatio.set(value)

                    elif key == 'Balanceratioy' and device.BalanceRatio.is_implemented() and device.BalanceRatio.is_writable():
                        if device is not None:
                            device.BalanceRatioSelector.set(1)
                            device.BalanceRatio.set(value)

                    elif key == 'Balanceratioz' and device.BalanceRatio.is_implemented() and device.BalanceRatio.is_writable():
                        if device is not None:
                            device.BalanceRatioSelector.set(2)
                            device.BalanceRatio.set(value)

                    elif key == 'Devicesn':
                        if device_sn != value:
                            try:
                                device.stream_off()
                            except:
                                pass

                            try:
                                device.close_device()
                            except:
                                pass
                            device = None
                            device_manager = None
                            device_sn = value

        if device is not None:
            raw_image = device.data_stream[0].get_image()
            if raw_image is not None and raw_image.get_status() == gxipy.GxFrameStatusList.SUCCESS:
                rgb_image = raw_image.convert(mode="RGB", flip=True)
                numpy_image = rgb_image.get_numpy_array()
                if image_queue.qsize() == 0:
                    image_queue.put(numpy_image)
            elif raw_image is None:
                try:
                    device.stream_off()
                except gxipy.gxiapi.UnexpectedError:
                    pass

                try:
                    device.close_device()
                except gxipy.gxiapi.InvalidHandle:
                    pass
                device = None
                device_manager = None
        else:
            numpy_image = numpy.random.randint(0, high=255, size=(256, 256, 4), dtype='uint8')
            if image_queue.qsize() == 0:
                image_queue.put(numpy_image)

    numpy_image = numpy.zeros(shape=(256, 256, 4), dtype='uint8')
    image_queue.put(numpy_image)

    if device is not None:
        try:
            device.stream_off()
        except gxipy.gxiapi.UnexpectedError:
            pass

        try:
            device.close_device()
        except gxipy.gxiapi.InvalidHandle:
            pass

    return


my_camera_params = {
    'Devicesn': me.parent().par.Devicesn.eval(),
    'Exposuretime': me.parent().par.Exposuretime.eval(),
    'Exposureauto': me.parent().par.Exposureauto.eval(),
    'Gain': me.parent().par.Gain.eval(),
    'Gainauto': me.parent().par.Gainauto.eval(),
    'Balancewhiteauto': me.parent().par.Balancewhiteauto.eval(),
    'Balanceratiox': me.parent().par.Balanceratiox.eval(),
    'Balanceratioy': me.parent().par.Balanceratioy.eval(),
    'Balanceratioz': me.parent().par.Balanceratioz.eval(),
}

op('results').clear()

my_request_queue = queue.Queue()
my_result_queue = queue.Queue()
my_image_queue = queue.Queue()

me.parent().store('request_queue', my_request_queue)
me.parent().store('result_queue', my_result_queue)
me.parent().store('image_queue', my_image_queue)
me.parent().storeStartupValue('request_queue', None)
me.parent().storeStartupValue('result_queue', None)
me.parent().storeStartupValue('image_queue', None)

my_thread = threading.Thread(target=camera_feed,
                             args=(my_request_queue, my_result_queue, my_image_queue, my_camera_params))

me.parent().store('thread', my_thread)
me.parent().storeStartupValue('thread', None)

# careful about running this more than once
# it will keep spawning threads
my_thread.start()
