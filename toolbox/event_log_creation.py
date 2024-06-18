import datetime
import os
import pandas as pd
import pm4py

import toolbox.preprocessing
from custom_exceptions import processStepNumberException

# Infos dazu https://pm4py.fit.fraunhofer.de/getting-started-page


def getProcessStepTime(input, index):
    '''
    Calculates timedelta in between different process steps

    :param input: framewise cluster

    :param index: index of current process step

    :return: time delta between process steps
    '''
    # FPS of video
    fps = float(toolbox.preprocessing.FPS_RESIZE)
    # Counter to determine which process step is looked at
    counterSteps = 0
    # Counter to determine number frames passed
    counterFrames = 0.0
    # Determine how many frames in concerned cluster
    for i in range(len(input)-1):
        if counterSteps == index:
            counterFrames += 1
        if input[i] != input[i+1]:
            counterSteps += 1
    seconds = counterFrames/fps
    roundSeconds = round(seconds)

    return roundSeconds


def createDF():
    '''
    Creates empty pandas Dataframe with event log columns and returns it

    :return: empty pandas Dataframe
    '''

    return pd.DataFrame(columns=("videoID", "activity","timestamp_start"))


def getProcessSteps(input, index):
    '''
    Returns the number of different process steps, of selected clustering

    :param input: numpy array with list of cluster numbers for each frame
    :param index: Index of the column of input, that is to be considered

    :return: Number of different process steps
    '''
    counter = 1
    for i in range(input.shape[0]-1):
        if input[i][index] != input[i+1][index]:
            counter += 1
    return counter


def exportCSV(dataframe, name, outputPath):
    '''
    Exports dataframe as eventlog in csv Format

    :param dataframe: Df including Eventlog
    '''
    event_log = pm4py.format_dataframe(dataframe, case_id='videoID', activity_key='activity', timestamp_key='timestamp_start')
    event_log.to_csv(os.path.join(outputPath, name+'_eventlog.csv'))


def exportXES(dataframe, name, outputPath):
    '''
    Exports dataframe as eventlog in XES Format

    :param dataframe: Df including Eventlog
    '''
    event_log = pm4py.format_dataframe(dataframe, case_id='videoID', activity_key='activity', timestamp_key='timestamp_start')
    pm4py.write_xes(event_log, os.path.join(outputPath, name+'_eventlog.xes'))


def extractLog(caseID, label, frameCluster, idx_selected):
    '''
    Extracts Event Log from video data collected

    :param caseID: case number of process instance
    :type caseID: int value

    :param label: numpy array with list of labels corresponding to their process step number
    :type label: numpy array

    :param frameCluster: numpy array with list of cluster numbers for each frame
    :type frameCluster: numpy array

    :param idx_selected: Index of the column of frameCluster, that is to be considered
    :type idx_selected: int
    :return:
    '''
    # Create dataframe for event log
    df = createDF()
    # Get number of process steps
    # First test if #process steps in label array equal to # process steps in frameCluster array
    processSteps = int(label[-1][0])
    test = int(getProcessSteps(frameCluster,idx_selected))
    print("Testwerte:", test, processSteps)
    if processSteps != test:
        raise processStepNumberException("Labeling Process not completed for every proess step")
    # Extract framewise cluster for selected process
    frameClusterCleaned = []
    for i in range(frameCluster.shape[0]):
        frameClusterCleaned.append(frameCluster[i][idx_selected])
    print(frameClusterCleaned)
    # Get timestamp for each process step
    starttime = datetime.datetime.now()
    timestamp = []
    for i in range(processSteps):
        if i == 0:
            timestamp.append('%s:%s:%s'%(starttime.hour, starttime.minute, starttime.second))
        else:
            timeStepPrevios = timestamp[-1]
            timeDelta = getProcessStepTime(frameClusterCleaned, i-1)
            previousTimeStamp = '%s-%s-%s'%(starttime.year, starttime.month, starttime.day) + ' ' + timeStepPrevios
            newStartTime = datetime.datetime.strptime(previousTimeStamp,'%Y-%m-%d %H:%M:%S' ) + datetime.timedelta(seconds=timeDelta)
            timestamp.append('%s:%s:%s'%(newStartTime.hour, newStartTime.minute, newStartTime.second))
    # Fill Dataframe
    for i in range(processSteps):
        df.loc[i] = [caseID, label[i][1], timestamp[i]]
    print(df)

    return df


def showProcessModel(data_path):
    log = pm4py.read_xes(data_path)

    process_tree = pm4py.discover_process_tree_inductive(log)
    bpmn_model = pm4py.convert_to_bpmn(process_tree)
    pm4py.view_bpmn(bpmn_model)
