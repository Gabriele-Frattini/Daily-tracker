import pandas as pd
import os
import dropbox
import io
from datetime import datetime

token = (Insert dropbox token here)
DBX = dropbox.Dropbox(token)

today = datetime.today().strftime('%Y-%m-%d')


def daily_tracker():

    # read in new data
    todays_data = {}
    todays_file = {}

    new_entries = DBX.files_list_folder(
        "/todays_data/"+"/"+today+"/"+today+"/").entries

    for path in [entry.path_lower for entry in new_entries]:
        _, todays_file[path] = DBX.files_download(path)

        with io.BytesIO(todays_file[path].content) as m:
            todays_data[path] = pd.read_csv(m)

         # read in old data

    _, file = DBX.files_download("/all_data/data.csv")

    with io.BytesIO(file.content) as m:
        old_data = pd.read_csv(m)

    # concatenate new data to df

    for key in [key for key in todays_data.keys()]:
        if 'respiratory rate' in key or 'audio exposure' in key or 'heart rate' in key or 'sleep analysis' in key or 'walking speed' in key:
            todays_data[key]["Date/Time"] = pd.to_datetime(
                todays_data[key]["Date/Time"])
            todays_data[key] = todays_data[key].set_index("Date/Time")
            todays_data[key] = todays_data[key].groupby(
                pd.Grouper(freq="h")).mean()

        else:
            todays_data[key]["Date/Time"] = pd.to_datetime(
                todays_data[key]["Date/Time"])
            todays_data[key] = todays_data[key].set_index("Date/Time")
            todays_data[key] = todays_data[key].groupby(
                pd.Grouper(freq="h")).sum()

    new_data = pd.DataFrame()
    for key in [key for key in todays_data.keys()]:
        new_data = pd.concat([new_data, todays_data[key]], axis=1)
    new_data = new_data.reset_index()

    # append new data to old data

    for i in todays_data.keys():
        data = old_data.append(todays_data[i])

    # Upload back to the dbx app's folder

    with io.BytesIO(data.to_csv(index=False).encode()) as enc_key:
        enc_key.seek(0)
        DBX.files_upload(enc_key.read(), path="/all_data/data.csv",
                         mode=dropbox.files.WriteMode.overwrite)


if __name__ == "__main__":
    daily_tracker()
