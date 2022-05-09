import socket
import os
import subprocess as sp
import argparse

import sys
import traceback
import argparse
import typing as typ
import random
import time
from fractions import Fraction

import numpy as np

from gstreamer import GstContext, GstPipeline, GstApp, Gst, GstVideo, GLib, GstVideoSink
import gstreamer.utils as utils


VIDEO_FORMAT = "RGB"
FPS = Fraction(30)
GST_VIDEO_FORMAT = GstVideo.VideoFormat.from_string(VIDEO_FORMAT)

BUFFER_SIZE = 4*1024

parser = argparse.ArgumentParser(description="Forward UDP port")
parser.add_argument("-a", dest="ip", required=True)
parser.add_argument("-p", dest="port", default=64155, type=int)
args = parser.parse_args()
print(args)

################################################## Utils

def fraction_to_str(fraction: Fraction) -> str:
    """Converts fraction to str"""
    return '{}/{}'.format(fraction.numerator, fraction.denominator)


def parse_caps(pipeline: str) -> dict:
    """Parses appsrc's caps from pipeline string into a dict

    :param pipeline: "appsrc caps=video/x-raw,format=RGB,width=640,height=480 ! videoconvert ! autovideosink"

    Result Example:
        {
            "width": "640",
            "height": "480"
            "format": "RGB",
            "fps": "30/1",
            ...
        }
    """

    try:
        # typ.List[typ.Tuple[str, str]]
        caps = [prop for prop in pipeline.split(
            "!")[0].split(" ") if "caps" in prop][0]
        return dict([p.split('=') for p in caps.split(',') if "=" in p])
    except IndexError as err:
        return None



################################################## UDP client
UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPSocket.sendto(b'hello', (args.ip, args.port)) 


################################################## Gstreamer
DEFAULT_CAPS = "\"application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96\""
DTYPE = utils.get_np_dtype(GST_VIDEO_FORMAT)


DEFAULT_PIPELINE = utils.to_gst_string([
    "appsrc emit-signals=True is-live=True caps={DEFAULT_CAPS}".format(**locals()),
    "queue",
	"rtph264depay", 
	"decodebin",
	"videoconvert",
	"autovideosink sync=false"
])


with GstContext():

    pipeline = GstPipeline(DEFAULT_PIPELINE)

    def on_pipeline_init(self):
        appsrc = self.get_by_cls(GstApp.AppSrc)[0]  # get AppSrc
        appsrc.set_property("format", Gst.Format.TIME)
        appsrc.set_property("block", True)


    pipeline._on_pipeline_init = on_pipeline_init.__get__(pipeline)

    try:
        pipeline.startup()
        appsrc = pipeline.get_by_cls(GstApp.AppSrc)[0]  # GstApp.AppSrc

        pts = 0  # buffers presentation timestamp
        duration = 10**9 / (FPS.numerator / FPS.denominator)  # frame duration
        while True:

            data, addr = UDPSocket.recvfrom(BUFFER_SIZE)
            array = [x for x in data]
            array = np.array(array, dtype=DTYPE)
            gst_buffer = utils.ndarray_to_gst_buffer(array)

            # set pts and duration to be able to record video, calculate fps
            pts += duration  # Increase pts by duration
            gst_buffer.pts = pts
            gst_buffer.duration = duration

            # emit <push-buffer> event with Gst.Buffer
            appsrc.emit("push-buffer", gst_buffer)

        appsrc.emit("end-of-stream")

        while not pipeline.is_done:
            time.sleep(.1)
    except Exception as e:
        print("Error: ", e)
    finally:
        pipeline.shutdown()

