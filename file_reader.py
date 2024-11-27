import pandas as pd

# Eyetracking ASC file rows (edit accordingly)
timestamp_row = 0
eye_x_row = 1
eye_y_row = 2



def read_eyelink_asc(filepath):
    # This function reads ONLY fixation coordinates
    fix_state = False
    temp_df = []
    f = open(filepath, "r")
    for line in f:
        row_list = list(line.split())
        if line[0].isalpha() == True:
            if row_list[0] == "SFIX":
                fix_state = True
            elif row_list[0] == "EFIX":
                fix_state = False
        if (line[0].isnumeric() == True) and (fix_state == True):
            new_row = [int(row_list[timestamp_row]), float(row_list[eye_x_row]), float(row_list[eye_y_row])]
            temp_df.append(new_row)
    eye_df = pd.DataFrame(temp_df, columns=["timestamp", "x", "y"])
    return eye_df

def read_objectdetection():
        pass



def is_inside_box(eye, box):
    eye_x = eye[0]
    eye_y = eye[1]

    min_x = box[0]
    min_y = box[1]
    max_x = min_x + box[2]
    max_y = min_y + box[3]

    return min_x <= eye_x <= max_x and min_y <= eye_y <= max_y

def is_closeby(eye, box):
    pass
    # TO DO closest neighbour with taking size on the screen into account

def sync_start_times(timestamp_start_eye, timestamp_start_obj):
    #TO DO: script for running object detecion and game in experiment needs to 
    # also record precise time and send MSG to eyelinker.
    # MSG in ASC file is going to have a precise timestamp in miliseconds
    # then you can kind of get precise measurments 
    pass
def sync_frame_time(timestamp_obj):
    # TO DO there is going to be less object detections frames than eyetracking data
    # this function looks for closest matching times in eye_df
    pass



if __name__ == "__main__":
    eye_df = read_eyelink_asc(r"C:\Users\agata\EyeTrackingAnnotator\data\mono250.asc")
    object_df = read_objectdetection(r"C:\Users\agata\EyeTrackingAnnotator\data\objtest.asc")