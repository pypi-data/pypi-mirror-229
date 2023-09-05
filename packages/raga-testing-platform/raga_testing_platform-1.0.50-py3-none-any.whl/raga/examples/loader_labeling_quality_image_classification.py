import ast
import csv
import pathlib
import re
from raga import *
import pandas as pd
import json
import datetime
import random

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def csv_parser(csv_file):
    pd_df = pd.read_csv(csv_file)
    dr = []
    inds = []
    for index, row in pd_df.iterrows():
        df = {}
        try:
            for index_r, column_name in enumerate(pd_df.columns):
                if column_name == "Ground Truth":
                    classification = ImageClassificationElement()
                    element = row[column_name]
                    
                    conf = ast.literal_eval(element)
                    for key, value in conf.items():
                        classification.add(key=key, value=value)
                    df["GroundTruth"] = classification
                    
                elif column_name == "mistake_score":
                    mistake_score = MistakeScore()
                    element = row[column_name]
                    conf = ast.literal_eval(element)

                    for key, value in conf.items():
                        mistake_score.add(key=key, value=value)
                    df["MistakeScore"] = mistake_score
                elif column_name == "ImageId":
                    element = row[column_name]
                    df[column_name] = element
                    file_name = row["SourceLink"].split("/")[-1]
                    df[column_name] = StringElement(f"{element}_{file_name}".replace(" ", "_"))
                    df["TimeOfCapture"] = TimeStampElement(get_timestamp_x_hours_ago(index_r))
                elif column_name == "SourceLink":
                    element = row[column_name]
                    df[column_name] = StringElement(element)
                    df["ImageUri"] = StringElement(f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/{element}")
                    

        except Exception as e:
                print(e)
                inds.append(index)
                continue
        dr.append(df)
    print("SKIP DATA POINTS", len(inds))
    return pd.DataFrame(dr)


pd_data_frame = pd.DataFrame(csv_parser("./assets/labelling_qc_score_df.csv"))


# data_frame_extractor(pd_data_frame).to_csv("./assets/labelling_qc_score_df_test.csv", index=False)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("GroundTruth", ImageClassificationSchemaElement(model="GT"))
schema.add("MistakeScore", MistakeScoreSchemaElement(ref_col_name="GroundTruth"))

run_name = f"run-failure-mode-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

#create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, name="100-sport-dataset-v11")

#load schema and pandas data frame
test_ds.load(data=pd_data_frame, schema=schema)