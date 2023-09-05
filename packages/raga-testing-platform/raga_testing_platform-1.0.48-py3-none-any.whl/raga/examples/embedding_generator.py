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
    for index, row in pd_df.iterrows():
        df = {}
        try:
            for index_r, column_name in enumerate(pd_df.columns):
                if column_name == "ModelA Inference":
                    pass
                elif column_name == "ModelB Inference":
                    classification = ImageClassificationElement()
                    element = row[column_name]
                    conf = ast.literal_eval(element)
                    classification.add("live", conf['live'])
                    df[column_name] = classification

                elif column_name == "Ground Truth":
                    classification = ImageClassificationElement()
                    element = row[column_name]
                    conf = ast.literal_eval(element)
                    classification.add("live", conf['live'])
                    df[column_name] = classification
                    
                elif column_name == "ImageVectorsM1":
                    ImageVectorsM1 = ImageEmbedding()
                    element = row[column_name]
                    element = json.loads(element)
                    for embedding in element:
                        ImageVectorsM1.add(Embedding(embedding))
                    df[column_name] = ImageVectorsM1

                elif column_name == "TimeOfCapture":
                    element = row[column_name]
                    df[column_name] = TimeStampElement(get_timestamp_x_hours_ago(index_r))
                elif column_name == "ImageId":
                    element = row[column_name]
                    df[column_name] = element
                    df["ImageUri"] = StringElement(f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/spoof/{element}")
                    df[column_name] = StringElement(element)
                elif column_name == "SourceLink":
                    df[column_name] = StringElement(element)

        except Exception as e:
                print(e)
                continue
        dr.append(df)
    return pd.DataFrame(dr)


# print(csv_parser("./assets/signzy_df.csv"))
pd_data_frame = pd.DataFrame(csv_parser("./assets/signzy_df.csv"))


# data_frame_extractor(pd_data_frame).to_csv("./assets/signzy_df_test.csv", index=False)



schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("ModelB Inference", ImageClassificationSchemaElement(model="modelB"))
schema.add("Ground Truth", ImageClassificationSchemaElement(model="GT"))

run_name = f"run-30-aug-failure-mode-analysis-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# # create test_session object of TestSession instance
# test_session = TestSession(project_name="LivenessDetection", run_name= run_name, access_key="xOVWFaP2fUB53jJkeflD", secret_key="RdhCitkCBLeq0YhA0VSlrSEeb8nbaVyKALF8dgBB", host="http://13.200.65.88:8080")

ModelExecutorFactory.getModelExecutor(model_name="OC", version="1", project_name="Tesr")

# test_session = TestSession(project_name="testingProject", run_name=run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080", u_test=True)
# test_session.project_id = 1
# test_session.experiment_id = 2308
# test_session.token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbkByYWdhIiwicm9sZXMiOlsiUk9MRV9BRE1JTiJdLCJ1c2VyTmFtZSI6ImFkbWluQHJhZ2EiLCJleHAiOjE2OTM0OTMzMTYsImlhdCI6MTY5MzQwNjkxNiwib3JnSWQiOjEsImp0aSI6ImFkbWluQHJhZ2EifQ.T1zJqPnFUHYXU9ZQLP-T5y4TT1m-5j8g95dlL6YoUIgYTyCKYV2QMVcDGVps78quZZ1MMx2ydMMBArwbcM--sg"

#create test_ds object of Dataset instance
# test_ds = Dataset(test_session=test_session, name="image-embedding-generator-ds")


# #load schema and pandas data frame
# test_ds.load(data=pd_data_frame, schema=schema)