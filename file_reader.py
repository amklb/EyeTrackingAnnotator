import pandas as pd



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
            elif row_list == "EFIX":
                fix_state = False
        if (line[0].isnumeric() == True) and (fix_state == True):
            new_row = [row_list[timestamp_row], row_list[eye_x_row], row_list[eye_y_row]]
            temp_df.append(new_row)
    eye_df = pd.DataFrame(temp_df, columns=["timestamp", "x", "y"])
    return eye_df

df = read_eyelink_asc(r"C:\Users\agata\EyeTrackingAnnotator\data\mono250.asc")
print(df)