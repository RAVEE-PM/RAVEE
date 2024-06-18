import cv2
import os
import time
from file_video_stream import FileVideoStream

# FPS, auf die Videos preprocessed werden
FPS_RESIZE = 15
# Width auf die Videos preprocessed werden
WIDTH_RESIZE = 640
# Height auf die Videos preprocessed werden
HEIGHT_RESIZE = 480

def ggT(z1,z2):
    '''
    Berechnet den ggT nach dem euklidischen Algorithmus
    ggT nutzen um Anzahl Frames für Reduktion zu errechnen
    :param z1: Zahl 1, ist ein int Wert
    :param z2: Zahl 2, ist ein int Wert
    :return: ggT als int Wert
    '''
    if z1>z2:
        dividend=z1
        divisor=z2
    else:
        dividend = z2
        divisor = z1
    if (dividend%divisor) != 0:
        divisor_neu = dividend%divisor
        dividend_neu=divisor
        return ggT(dividend_neu,divisor_neu)
    else:
        return divisor


def kuerzen(z1,z2,ggT):
    '''
    Kürzt die beiden übergebenen Zahlen mit dem ggT
    nutzen um Anzahl Frames für Reduktion zu errechnen
    :param z1: erster zu kürzender Wert
    :param z2: zweiter  zu kürzender Wert
    :param ggT: der ggT der beiden Werte, um den gekürzt wird
    :return: die beiden gekürzten Werte der Zahlen z1 & z2
    '''
    z1_gekuerzt = z1/ggT
    z2_gekuerzt = z2/ggT
    return z1_gekuerzt,z2_gekuerzt


def reduce_video_size(input_path, output_path, caseID, videoName):
    new_output_path = os.path.join(output_path, str(caseID)+'_'+videoName+"_reduced.avi")
    # start file video stream thread
    fvs = FileVideoStream(input_path).start()
    print(fvs.fps)
    # allow buffer to start to fill
    time.sleep(1.0)
    # Checks fps for possible need to reduce
    reduceFPS = (fvs.fps > FPS_RESIZE)
    width = fvs.width
    height = fvs.height
    resize = width > WIDTH_RESIZE and height > HEIGHT_RESIZE
    if reduceFPS:
        fps = fvs.fps
        print("FPS:", fps)
        print("Width:", fvs.width)
        print("Height:", fvs.height)
        tl = fps - FPS_RESIZE
        ggT_value = ggT(fps, tl)
        wert1, wert2 = kuerzen(fps, tl, ggT_value)
        raus_je_iteration = wert2
        rein_je_iteration = wert1
        aktuell_raus = 0
        aktuell_rein = 0
    if resize:
        writer = cv2.VideoWriter(new_output_path,
                                 cv2.VideoWriter_fourcc(*"MJPG"), FPS_RESIZE, (WIDTH_RESIZE, HEIGHT_RESIZE))
    else:
        writer = cv2.VideoWriter(new_output_path,
                                 cv2.VideoWriter_fourcc(*"MJPG"), FPS_RESIZE, (width,height))
    # loop over frames from video file stream
    while fvs.more():
        # grab the frame from the threaded video file stream
        frame = fvs.read()
        # Resize Image if necessary
        frame_resized = frame
        if resize:
            frame_resized = cv2.resize(frame, (WIDTH_RESIZE, HEIGHT_RESIZE), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        # Reduce FPS if necessary
        if reduceFPS:
            if aktuell_rein < rein_je_iteration:
                frame_used = frame_resized
                writer.write(frame_used)
                aktuell_rein += 1
            elif aktuell_raus < raus_je_iteration:
                frame_trash = frame_resized
                aktuell_raus += 1
            else:
                aktuell_raus = 0
                frame_used = frame_resized
                aktuell_rein = 1
                writer.write(frame_used)
        else:
            writer.write(frame_resized)
    writer.release()

