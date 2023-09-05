import csv
import pathlib
from raga import *
import pandas as pd
import json
import datetime
import random

label_to_classname = {
    0: "no_data",
    1: "water",
    2: "trees",
    3: "grass",
    4: "flooded vegetation",
    5: "crops",
    6: "scrub",
    7: "built_area",
    8: "bare_ground",
    9: "snow_or_ice",
    10: "clouds",
}

def generate_random_roadside_class():
    classes = [
        "fruits",
        "vegetables",
        "dairy products",
        "meat",
        "seafood",
        "canned goods",
        "bakery items",
        "beverages",
        "snacks",
        "cereals",
        "spices",
        "frozen foods",
        "deli items",
        "cleaning supplies",
        "personal care",
        "household essentials",
        "pet supplies",
        "baby care",
        "health and wellness",
        "condiments"
        # Add more classes as needed
    ]
    return random.choice(classes)

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def generate_random_float_list(length=18, min_value=0.0, max_value=500):
    if length <= 10:
        raise ValueError("Length should be greater than 10")
    random_list = [round(random.uniform(min_value, max_value),1) for _ in range(length)]
    return random_list

def generate_random_bbox_xywh():
    x = random.uniform(0, 1)
    y = random.uniform(0, 1)
    width = random.uniform(0, 1 - x) 
    height = random.uniform(0, 1 - y)
    return x, y, width, height

def parseLossFile(csv_file_path):
    df = pd.read_csv(csv_file_path)
    f2l = {}
    file_paths = []
    for index, row in df.iterrows():

        if row['label'] not in label_to_classname:
            continue

        file_path = row['filepath']
        if file_path not in f2l:
            file_paths.append(file_path)
            f2l[file_path] = []
        f2l[file_path].append([row['label'], float(row['loss'])])

    return file_paths, f2l


def generate_data_frame(file_paths, f2l):
    data = []
    for filepath in file_paths:

        annotations = SemanticSegmentationObject()
        mistake_score = MistakeScore()
        AnnotationsV1 = ImageDetectionObject()

        for i, item in enumerate(f2l[filepath]):
            if item[0] not in label_to_classname:
                continue
            label = label_to_classname[item[0]]
            annotations.add(SemanticSegmentation(Id=i, LabelId=item[0], LabelName=label, Segmentation=generate_random_float_list(), Confidence=1, Format="xn,yn_normalised"))
            mistake_score.add(id=item[0], values=item[1])
            AnnotationsV1.add(ObjectDetection(Id=0, ClassId=0, ClassName=generate_random_roadside_class(), Confidence=round(random.uniform(0, 1), 1), BBox=generate_random_bbox_xywh(), Format="xywh_normalized"))

        image_url = f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/satsure_rgb/data_points/{pathlib.Path(filepath).stem}/images/{filepath}"
        mask_url = f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/satsure_lulc/data_points/{pathlib.Path(filepath).stem}/images/{filepath}"
        timestamp = get_timestamp_x_hours_ago(i)
        data_point = {
            'ImageId': StringElement(filepath),
            'ImageUri': StringElement(image_url),
            'TimeOfCapture': TimeStampElement(timestamp),
            'SourceLink': StringElement(filepath),
            'Annotations': StringElement(mask_url),
            # 'SemanticSegmentation':annotations,
            # 'ObjectDetection':AnnotationsV1,
            'MistakeScores': mistake_score,
            'Reflection': StringElement('Yes'),
            'Overlap': StringElement('Yes'),
            'CameraAngle': StringElement('Top')
        }
        data.append(data_point)
    return pd.DataFrame(data)

csv_file = "./assets/final_image_1000.csv"

file_paths, f2l = parseLossFile(csv_file)
df = generate_data_frame(file_paths, f2l)
# df = data_frame_extractor(generate_data_frame(file_paths, f2l)).to_csv("./assets/final_image_loss_10000_df.csv", index=False)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("Annotations", TIFFSchemaElement(label_mapping=label_to_classname, schema="tiff"))
schema.add("MistakeScores", MistakeScoreSchemaElement(ref_col_name="Annotations"))
schema.add('Reflection', AttributeSchemaElement())
schema.add('Overlap', AttributeSchemaElement())
schema.add('CameraAngle', AttributeSchemaElement())



run_name = f"run-labeling-quality-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")
# # #create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, name="satsure-1000-data-points-v4")

# #load schema and pandas data frame
test_ds.load(data=df, schema=schema)
