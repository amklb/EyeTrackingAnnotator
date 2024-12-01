import pandas as pd
import numpy as np
from math import dist

# Paths to data files
path_eyelink_data = r"data\mono250.asc"
path_object_data = r"data\data_obj.txt"

# Eyetracking ASC file rows (edit accordingly)
timestamp_row = 0
eye_x_row = 1
eye_y_row = 2
# Put in desired MSG to sync up with
start_event = "START"

# Allowed difference marigin between 
# eyelink timestamp and object detection 
# timestamp in miliseconds (edit to liking)
# p.s. it's both ways (future and past) 
allowed_time_margin = 5


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

def read_objectdetection(filepath):
    # Silly simple: open df that was prepared in obj_detection.py
    df = pd.read_csv(filepath, sep = "\t")
    return df


def is_inside_box(eye, box):
    # Recognise if gaze is in the box of detected object
    eye_x = eye[0]
    eye_y = eye[1]

    min_x = box[0]
    min_y = box[1]
    max_x = min_x + box[2]
    max_y = min_y + box[3]

    return min_x <= eye_x <= max_x and min_y <= eye_y <= max_y

def is_closeby(eye, box):
    # Checks distance from gaze to centre of detected object
    # if gaze is inside object detection box, this function will
    # not be called, and the value in df is gonna be set to 0 
    top_left_x = box[0]
    top_left_y = box[1]
    width = box[2]
    height = box[3]
    center = (int(width/2 + top_left_x), int(height/2 + top_left_y))
    distance_from_centre = dist(eye, center)
    return distance_from_centre

def sync_start_times(filepath, df):
    # Sync of time in object dataframe and eyetracking dataframe
    # based on eyelink event (inserted on top of the file) that should
    # also run the detection script during an experiment
    start_time = 0
    f = open(filepath, "r")
    for line in f:
        row_list = list(line.split())
        if start_event in row_list:
            start_time = int(row_list[1])
            break
    df["sync_time"] = df["timestamp"].map(lambda timestamp : timestamp - start_time)
    return df
    
def sync_frame_time(timestamp_obj, e_df):
    # There is going to be less object 
    # detections frames than eyetracking data.
    # This function looks for closest 
    # matching times in eye_df
    max_time = timestamp_obj + allowed_time_margin
    min_time = timestamp_obj - allowed_time_margin

    exact_match = e_df[e_df["sync_time"] == timestamp_obj]
    if exact_match.empty == False:
        exact_match = exact_match.values.flatten().tolist()
        return exact_match
    else:
        closest_match = e_df.iloc[(e_df["sync_time"]-timestamp_obj).abs().argsort()[:1]]
        print(closest_match["sync_time"].values[0])
        if  min_time <= closest_match["sync_time"].values[0] <= max_time:
            closest_match = closest_match.values.flatten().tolist()
            return closest_match
        else:
            return -1




if __name__ == "__main__":
    # load datasets
    eye_df = read_eyelink_asc(path_eyelink_data)
    object_df = read_objectdetection(path_object_data)
    print(object_df.head())
    print(eye_df.head())
    #sync eyelink time in miliseconds
    eye_df = sync_start_times(path_eyelink_data, eye_df)
    print(eye_df.head())

    # for every appearing object check if person is looking
    looking_at_column = []
    looking_close_column = []
    eye_timestamp_id_column = []
    for row in object_df.itertuples():
        current_eye = sync_frame_time(row.time, eye_df)
        if current_eye == -1:
            looking_at_column.append(None)
            looking_close_column.append(None)
            eye_timestamp_id_column.append(None)
        else:
            eye_timestamp_id_column.append(int(current_eye[0]))
            eye_position = [current_eye[1], current_eye[2]]
            box_position = [row.x, row.y, row.w, row.h]
            looking = is_inside_box(eye_position, box_position)
            looking_at_column.append(int(looking))
            if looking == True:
                looking_close_column.append(0)
            else:
                looking_close = is_closeby(eye_position, box_position)
                looking_close_column.append(int(looking_close))
    object_df["looking_at"] = looking_at_column
    object_df["distance_from_box"] = looking_close_column
    object_df["eye_time_id"] = eye_timestamp_id_column

object_df.to_csv(r'C:\Users\agata\EyeTrackingAnnotator\data\correlations.txt', sep=',', index=False)
print('Finished.')



   