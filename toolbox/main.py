import os
import shutil
import subprocess
import pandas as pd
import numpy as np
import time
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
import cv2

from finch.finch import FINCH
from gui import gui_elements
from preprocessing import reduce_video_size
from feature_extraction import extract_framewise_features
from display_video_snippets import run_snippets
from event_log_creation import extractLog, createDF
from event_log_creation import showProcessModel
from event_log_creation import exportCSV, exportXES



# Directories for runtime
# Current working directory
currentDirectory = os.getcwd()
# System specific seperator
seperator = str(os.path.sep)
# Directory of IDT feature extraction
targetIDT = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'IDT'))
# Get Video input directory
raw_video_input = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'video_input'))
# Get directory for processed Video Output
processedVideoOutput = os.path.abspath(os.path.join(currentDirectory, os.pardir, 'IDT', 'data'))
# Get directory for IDT Output
idtOutput = os.path.abspath(os.path.join(currentDirectory, os.pardir, 'IDT', 'features'))
# Get directory for FV Output
fvOutput = os.path.abspath(os.path.join(currentDirectory, os.pardir, 'finch', 'input'))
# Get directory for FINCH Output
finchOutput = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'finch', 'output'))
# Get directory with demo files
demoPath = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'DemoFiles'))
# Get directory for eventlog output
eventlogOutput = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'EventLog_Output'))
# Eventlog output for DemoFiles
eventlogOutputDemo = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'DemoFiles'))
# Temporary Directory to cache results if necessary
tempDirectoryPath = os.path.abspath(os.path.join(currentDirectory,os.pardir, 'temp'))

# Amount of clusters to be retrieved by FINCH
required_cluster = None
# CaseID counter
CASEID = 1
# Demo-Mode, if True runs DemoFiles
DEMO = True


def concatenate(video_clip_paths, output_path, method="compose"):
    # create VideoFileClip object for each video file
    clips = [VideoFileClip(c) for c in video_clip_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    # write the output video file
    final_clip.write_videofile(output_path)


def getFrameCount(video_clip_path):
    cap = cv2.VideoCapture(video_clip_path)
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


def main():

    if DEMO:
        # Runs the Code starting with labeling process on a precomputed feature set of a certain video
        # Import necessary demo files
        video_path = os.path.join(demoPath,'scan_video_reduced.avi')
        c = np.genfromtxt(os.path.join(demoPath, 'scan_video_reduced_c.csv'),delimiter=',')
        num_cluster = np.genfromtxt(os.path.join(demoPath, 'scan_video_reduced_num_cluster.csv'), delimiter=',')
        # Get User Input for label
        idx_selected = run_snippets(video_path, c, num_cluster)
        label = np.array(list(gui_elements.LABEL.items()))
        print("Label",label)
        # Reset Label variable
        gui_elements.LABEL.clear()
        gui_elements.counter = 1
        caseID = 1
        # Get Event Log as dataframe
        df = extractLog(caseID, label, c, idx_selected)
        # Export Eventlog
        exportXES(df, 'scan_video_reduced', eventlogOutputDemo)
        exportCSV(df, 'scan_video_reduced', eventlogOutputDemo)
        # Build image of process tree
        showProcessModel(os.path.join(eventlogOutputDemo, 'scan_video_reduced_eventlog.xes'))




    else:
        # Iterate over all Input data & Preprocess
        for count, value in enumerate(os.listdir(raw_video_input)):

            # As for the BF-Dataset, we reduce overall data amount by down-sampling all
            # videos to a resolution of 620x480 pixels with a frame rate of 15 fps
            # see:https://serre-lab.clps.brown.edu/resource/breakfast-actions-dataset/
            file_path = os.path.join(raw_video_input, value)
            video_name = os.path.splitext(os.path.split(file_path)[1])[0]
            global CASEID
            caseID = CASEID
            CASEID += 1
            reduce_video_size(file_path, processedVideoOutput, caseID, video_name)
           #reduce_video_size(file_path, tempDirectoryPath, caseID, video_name)   #If all videos are merged - use this instead of above line
            print(f'Completed {value}')
            if (count + 1) % 10 == 0:
                print(f'{count + 1} files were completed.')

        # #Iterate over all preprocessed video data & concatenate them
        # #Retrieve Number of frames for every video sequence & save in list, as well as
        # #starting frame for every video sequence in merged video
        # method = "compose"
        # video_clip_path = []
        # frame_count = []
        # start_frame = []
        # for count, value in enumerate(os.listdir(tempDirectoryPath)):
        #     file_path = os.path.join(tempDirectoryPath, value)
        #     frame_count.append(getFrameCount(file_path))
        #     if not start_frame:
        #         start_frame.append(1.0)
        #     else:
        #         last_value = start_frame[-1]
        #         start_frame.append(last_value + frame_count[-2])
        #     video_clip_path.append(file_path)
        # output_clip_path = os.path.join(processedVideoOutput, 'concatenated_video.avi')
        # concatenate(video_clip_path, output_clip_path, method)

        # The following code is executing the Python Wrapper for the Improved-Dense-Trajectories (IDT)
        # Further description of the Python Wrapper: https://github.com/AraMambreyan/Improved-Dense-Trajectories/blob/master/README.md
        # run command to create IDT via docker
        os.chdir(targetIDT)
        subprocess.run('docker build -t idt .')
        subprocess.run('docker run -v ' + targetIDT + seperator + 'features:/densetrack/features idt')

        # Compute framewise FV for all the IDT-Features extracted
        # Dictionary,that includes all the computed FV
        compFV = {}
        for count, value in enumerate(os.listdir(idtOutput)):
            file_path = os.path.join(idtOutput, value)
            nameFV = os.path.splitext(os.path.split(file_path)[1])[0]
            print("NameFV",nameFV)
            caseNr = int(nameFV.split('_')[0])
            print("CaseNr",caseNr)
            videoNameList = nameFV.split('_')[1:-1]
            print("VideoName",videoNameList)
            videoName = '_'.join(videoNameList)
            key = str(caseNr)+'-'+videoName
            print("key",key)
            features = extract_framewise_features(file_path, fvOutput)
            compFV[key] = features
            print(f'Completed {value}')
            if (count + 1) % 10 == 0:
                print(f'{count + 1} files were completed.')

        # The following Code_Artefact runs the FINCH-Algorithm
        # Create dataframe to create eventlog
        eventlog = createDF()
        # Further description of the TW-FINCH-Algorithm here: https://github.com/ssarfraz/FINCH-Clustering/tree/master/TW-FINCH
        for key, value in compFV.items():
            start = time.time()
            # start FINCH
            if required_cluster is not None:
                c, num_clust, req_c = FINCH(value, req_clust=required_cluster, tw_finch=True)
            else:
                c, num_clust, req_c = FINCH(value, req_clust=None, tw_finch=True)

            print('Time Elapsed: {:2.2f} seconds'.format(time.time() - start))

            # Save FINCH data to output directory
            # Get Name of video
            name = key.split('-')[1]
            # Get KeyNr of video
            keyNr = key.split('-')[0]
            print('Writing back the results on the provided path ...')
            np.savetxt(os.path.join(finchOutput, name + '-c.csv'), c, delimiter=',', fmt='%d')
            np.savetxt(os.path.join(finchOutput, name + '-num_cluster.csv'), np.array(num_clust), delimiter=',',
                       fmt='%d')
            if req_c is not None:
                np.savetxt(os.path.join(finchOutput, name + '-req_c.csv'), req_c, delimiter=',', fmt='%d')


            # Following code is running the labeling Module for each video analysed by FINCH
            # Get path to reduced video w keyNr
            for count, value in enumerate(os.listdir(processedVideoOutput)):
                vName = value
                print("vName",vName)
                keyVName = vName.split('_')[0]
                if keyNr == keyVName:
                    video_path_Name = value
            video_path = os.path.join(processedVideoOutput, video_path_Name)
            print(video_path)
            if req_c is None:
                idx_selected = run_snippets(video_path, c, num_clust)
            else:
                idx_selected = run_snippets(video_path, c, num_clust, req_c)
            # Grab user-defined labels
            label = np.array(list(gui_elements.LABEL.items()))
            print(label)
            # Reset Label variable
            gui_elements.LABEL.clear()
            gui_elements.counter = 1
            # Get elements for XES extraction
            caseID = int(keyNr)

            # Following Code is running the EventLog creation and Extraction
            # aswell as showing the final process tree
            df = extractLog(caseID, label, c, idx_selected)
            eventlog = pd.concat([eventlog, df], axis=0, ignore_index=1)

            print(f'Completed {value}')
            if (count + 1) % 10 == 0:
                print(f'{count + 1} files were completed.')

        exportCSV(eventlog, '', eventlogOutput)
        exportXES(eventlog, '', eventlogOutput)
        showProcessModel(os.path.join(eventlogOutput,"_eventlog.xes"))

        # Delete all features in idtOutput
        for filename in os.listdir(idtOutput):
            file_path = os.path.join(idtOutput, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Delete all features in fvOutput
        for filename in os.listdir(fvOutput):
            file_path = os.path.join(fvOutput, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Delete all Videos in processedVideoOutput
        for filename in os.listdir(processedVideoOutput):
            file_path = os.path.join(processedVideoOutput, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))



if __name__ == "__main__":
    main()