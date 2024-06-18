import os

import cv2
import sys
import time
from custom_exceptions import VersionException
from threading import Thread

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue
else:
    raise VersionException("Install a Python Version >= 3")


class FileVideoStream:
    '''
    Class for pre-processing videos

    Includes imutils version for fast frame reading using queues
    https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/

    '''

    def __init__(self, path, queue_size=128):
        '''
        Initialize the class
        :param path: path to the video file
        :param queue_size: the size of the FIFO-Queue later to be initialized - limits the number
                           of items, that can be placed in the threading-list. Default value is set
                           to 128 frames
        '''

        # initialize the file video stream along with a boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stopped = False

        #Get video attributes
        self.width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)
        self.num_frames = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
        # For video length cv2.CAP_PROP_POS_MSEC seems to be unreliable
        # see: https://github.com/opencv/opencv/issues/15749#
        self.video_length_seconds = self.num_frames/self.fps

        # initialize the queue used to store frames read from
        # the video file
        self.video_queue = Queue(maxsize=queue_size)

    def start(self):
        '''
        Starts a thread seperate to the main thread
        :return: self - thread instance, that has been started
        '''
        # start a thread to read frames from the video file stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        '''
        Reads and decodes frames from the video file, along with maintaining the actual
        queue structure
        :return:
        '''
        # Prints process ID of current process
        print(str(os.getpid()),":Starting Update")
        # Keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            # otherwise ensure queue has room in it
            if not self.video_queue.full():
                #read the next frame from file
                (grabbed, frame) = self.stream.read()

                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file and do not add an item to the queue
                if not grabbed:
                    self.stopped = True

                else:

                    # add the frame to the queue
                    self.video_queue.put(frame)

            else:
                #Rest for 10ms, queue is full
                time.sleep(0.1)

        self.stream.release()

    def read(self):
        '''
        Returns next frame in queue
        :return: Next frame from queue
        '''
        return self.video_queue.get()

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of
    # file stream.
    def running(self):
        return self.more() or not self.stopped

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.video_queue.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.1)
            tries += 1

        # fixed error of none element
        return self.video_queue.qsize() > 0 and self.video_queue.queue[0] is not None

    def join(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()
        print(str(os.getpid()) + ": FileVideoStream joined")

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True



# data = "C:\\Users\\nikla\\Documents\\scan_video.avi"
#
#
# def video_preprocessing(dataPath):
#     '''
#
#     :param dataPath:
#     :return:
#     '''
#     vidcap = cv2.VideoCapture(dataPath)
#     num_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
#     fps = int(vidcap.get(cv2.CAP_PROP_FPS))
#     print("Anzahl ges. Frames:",num_frames)
#     print("FPS:",fps)
#
#     if fps > 15:
#         vidcap.set(int(cv2.CAP_PROP_FPS), 15)
#         print("FPS angepasst auf",int(vidcap.get(cv2.CAP_PROP_FPS)))
#
#
# video_preprocessing(data)
