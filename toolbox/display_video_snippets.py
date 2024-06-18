import cv2
import numpy as np
from gui import gui_elements
from collections import Counter
from custom_exceptions import idxSelectionError

def display_video_snippet(video_path, start_frame, end_frame):
    stream = cv2.VideoCapture(video_path)
    start = start_frame
    ende = end_frame
    stream.set(cv2.CAP_PROP_POS_FRAMES, start)
    while (stream.isOpened()):
        ret, frame = stream.read()
        aktueller_frame = str(stream.get(cv2.CAP_PROP_POS_FRAMES))
        # describe the type of font
        # to be used.
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Use putText() method for
        # inserting text on video
        cv2.putText(frame,
                    aktueller_frame,
                    (50, 50),
                    font, 1,
                    (0, 255, 255),
                    2,
                    cv2.LINE_4)
        if float(aktueller_frame) > ende:
            break
        else:
            cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # by press 'q' you quit the process
            break  #

    gui_elements.inputboxLine()
    stream.release()
    cv2.destroyAllWindows()

# The following code returns video snippets to the user to label them
def run_snippets(video_path, c,num_clust,req_c=None):
    # Initialize variable
    ges_cluster = np.array([0])
    # Normal way:
    idx_selected = 'Fehler'
    if req_c is None:
        # Let user select amount of clusters he deems appropriate from prepared cluster-set
        # User-Input, which clustering should be chosen
        gui_elements.setOptions(num_clust)
        gui_elements.inputboxList()
        num_cluster = gui_elements.NUM_CLUSTER
        if num_cluster == 0:
            print("Verarbeitungsfehler")
        # Retrieves amount of different clusters (for comparison with user-input)
        # and compares both. If a match is found, continue with clustering for this match
        for i in range(c.shape[1]):
            templist = np.array([c[j][i] for j in
                            range(c.shape[0])])
            num_diff_clust = len(Counter(templist).keys())
            if num_diff_clust == int(float(num_cluster)):
                idx_selected = i
                ges_cluster = templist
                break
    else:
        # Use output of req_c
        ges_cluster = req_c
        req_c_sorted = np.sort(ges_cluster, axis = -1)
        idx_selected = req_c_sorted[-1]+1

    # Wait unitl user is ready
    gui_elements.popupmsg("Click to continue","Ready for Videolabeling?")
    # Grab clusternumber and last frame of cluster
    cluster_assignment = []
    for i in range(ges_cluster.shape[0] - 1):
        cluster = ges_cluster[i]
        # If the following cluster is not equal to the present one, then
        # add the current one as end frame to the output
        if ges_cluster[i] != ges_cluster[i + 1]:
            cluster_assignment.append([cluster, i])
        # The last cluster should also be added to the output (even if it
        # has no successor to which it could be unequal to).
        if i == int(ges_cluster.shape[0] - 2):
            cluster = ges_cluster[i + 1]
            cluster_assignment.append([cluster, i + 1])
    print(cluster_assignment)
    for i in range(len(cluster_assignment)):
        # Grab cluster number for which we watch a video snippet
        cluster = cluster_assignment[i][0]
        # Grab index of last frame of said cluster
        idx_end_frame = cluster_assignment[i][1]
        # Grab index of first frame of said cluster
        if i == 0:
            idx_first_frame = 0
        else:
            idx_first_frame = cluster_assignment[i-1][1]+1
        print("Cluster Nr:",cluster, "1.Frame:",idx_first_frame, "letzter Frame:",idx_end_frame)
        display_video_snippet(video_path, idx_first_frame, idx_end_frame)
    if idx_selected == 'Fehler':
        raise idxSelectionError("Fehler bei Übergabe des Index des ausgewählten Cluster")
    return idx_selected
