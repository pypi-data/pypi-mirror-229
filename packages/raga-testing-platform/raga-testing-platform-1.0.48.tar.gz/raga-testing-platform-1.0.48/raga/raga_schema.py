from abc import ABC
import json
from typing import Optional
from datetime import datetime
import pandas as pd

class RagaSchemaElement(ABC):
    def __init__(self):
        self.type = ""
        self.model = ""
        self.ref_col_name = ""
        self.label_mapping = {}
        self.schema = ""

class PredictionSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "imageName"

class ImageUriSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "imageUri"

class MaskUriSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "maskUri"

class TimeOfCaptureSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "timestamp"

class FeatureSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "feature"
class AttributeSchemaElement(RagaSchemaElement):
    def __init__(self):
        super().__init__()
        self.type = "attribute"

class InferenceSchemaElement(RagaSchemaElement):
    def __init__(self, model:str):
        super().__init__()
        if not isinstance(model, str) or not model: 
            raise ValueError("model is required and must be a non-empty string.")
        self.type = "inference"
        self.model = model

class ImageEmbeddingSchemaElement(RagaSchemaElement):
    def __init__(self, model:str="", ref_col_name:str=""):
        super().__init__()
        self.type = "imageEmbedding"
        self.model = model
        self.ref_col_name = ref_col_name


class ImageClassificationSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, ref_col_name:str=""):
        super().__init__()
        if not isinstance(model, str) or not model: 
            raise ValueError("model is required and must be a non-empty string.")
        self.type = "classification"
        self.model = model
        self.ref_col_name = ref_col_name

class TIFFSchemaElement(RagaSchemaElement):
     def __init__(self, label_mapping:dict, schema:str=""):
        super().__init__()
        if not isinstance(label_mapping, dict) or not label_mapping: 
            raise ValueError("model is required and must be a non-empty string.")
        # Check that the label_mapping keys are integers and values are strings
        for key, value in label_mapping.items():
            if not isinstance(key, int) or not isinstance(value, str):
                raise ValueError("label_mapping keys must be integers and values must be strings.")
        self.type = "blob"
        self.label_mapping = label_mapping
        self.schema = schema

class SemanticSegmentationSchemaElement(RagaSchemaElement):
     def __init__(self):
        super().__init__()
        self.type = "imageSegmentation"

class RoiEmbeddingSchemaElement(RagaSchemaElement):
    def __init__(self, model:str, ref_col_name:str=""):
        super().__init__()
        if not isinstance(model, str) or not model: 
            raise ValueError("model is required and must be a non-empty string.")
        self.type = "roiEmbedding"
        self.model = model
        self.ref_col_name = ref_col_name

class MistakeScoreSchemaElement(RagaSchemaElement):
    def __init__(self, ref_col_name:str=""):
        super().__init__()
        self.type = "mistakeScores"
        self.ref_col_name = ref_col_name



class RagaSchema():
    def __init__(self):
        self.columns = list()

    def validation(self, column_name: str, ragaSchemaElement:RagaSchemaElement):
        if not isinstance(column_name, str) or not column_name: 
            raise ValueError("column_name is required and must be a non-empty string.")
        if not isinstance(ragaSchemaElement, RagaSchemaElement): 
            raise ValueError("ragaSchemaElement must be an instance of the RagaSchemaElement.")
        return True
     
    def add(self, column_name: str, ragaSchemaElement:RagaSchemaElement):
        self.validation(column_name, ragaSchemaElement)
        self.columns.append({"customerColumnName":column_name, "type":ragaSchemaElement.type, "modelName":ragaSchemaElement.model, "refColName":ragaSchemaElement.ref_col_name, "columnArgs":{"labelMapping":ragaSchemaElement.label_mapping, "schema":ragaSchemaElement.schema}})

class StringElement():
    def __init__(self, value:str):
        self.value = value

    def get(self):
        return self.value
    
class FloatElement():
    def __init__(self, value:float):
        self.value = value

    def get(self):
        return self.value
    
class TimeStampElement():
    def __init__(self, date_time:datetime):
        self.date_time = date_time

    def get(self):
        return self.date_time
    
class AggregationLevelElement():
    def __init__(self):
        self.levels = []

    def add(self, level:str):
        assert isinstance(level, str) and level, "level is required and must be str."
        self.levels.append(level)

    def get(self):
        return self.levels
    
class ModelABTestTypeElement():
    def __init__(self, type:str):
        self.type = type
        if self.type not in ["labelled", "unlabelled"]:
            raise ValueError("Invalid value for 'type'. Must be one of: ['labelled', 'unlabelled'].")

    def get(self):
        return self.type    

       
class ModelABTestRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, IoU:float, _class:str, threshold:float):
        assert isinstance(metric, str) and metric, "metric is required and must be str."
        assert isinstance(_class, str) and _class, "_class is required and must be str."
        assert isinstance(IoU, float) and IoU, "IoU is required and must be float."
        assert isinstance(threshold, float) and threshold, "threshold is required and must be float."
        self.rules.append({ "metric" : metric, "iou": IoU,  "class": _class, "threshold":threshold })

    def get(self):
        return self.rules
    
class FMARules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, metric_threshold:float, label:str, conf_threshold:float):
        assert isinstance(metric, str) and metric, "metric is required and must be str."
        assert isinstance(label, str) and label, "label is required and must be str."
        assert isinstance(conf_threshold, float) and conf_threshold, "conf_threshold is required and must be float."
        assert isinstance(metric_threshold, float) and metric_threshold, "metric_threshold is required and must be float."
        self.rules.append({ "metric" : metric, "threshold": metric_threshold,  "clazz": [label], "confThreshold":conf_threshold })

    def get(self):
        return self.rules
    
class LQRules():
    def __init__(self):
        self.rules = []

    def add(self, metric:str, metric_threshold:float, label:list):
        assert isinstance(metric, str) and metric, "metric is required and must be str."
        assert isinstance(label, list) and label, "label is required and must be list."
        assert isinstance(metric_threshold, float) and metric_threshold, "metric_threshold is required and must be float."
        self.rules.append({ "metric" : metric, "threshold": metric_threshold,  "clazz": label})

    def get(self):
        return self.rules
    
class DriftDetectionRules():
    def __init__(self):
        self.rules = []

    def add(self, type:str, dist_metric:str, _class:str, threshold:float):
        assert isinstance(dist_metric, str) and dist_metric, "metric is required and must be str."
        assert isinstance(_class, str) and _class, "_class is required and must be str."
        assert isinstance(threshold, float) and threshold, "threshold is required and must be float."
        self.rules.append({ "type" : type, "dist_metric" : dist_metric,  "class": _class, "threshold":threshold })

    def get(self):
        return self.rules
    
class SemanticSegmentation:
    def __init__(self, Id:Optional[str], Format:Optional[str], Confidence:Optional[float], LabelId:Optional[str] = None, LabelName:Optional[str]=None, Segmentation=[]):
        self.Id = Id
        self.LabelId = LabelId
        self.LabelName = LabelName
        self.Segmentation = Segmentation
        self.Format = Format
        self.Confidence = Confidence

class SemanticSegmentationObject():
    def __init__(self):
        self.segmentations = list()
    
    def add(self, segmentations:SemanticSegmentation):
        self.segmentations.append(segmentations.__dict__)
    
    def get(self):
        return self.__dict__
    
class MistakeScore:
    def __init__(self):
         self.mistake_scores = dict()

    def add(self, id, values: list):
        self.mistake_scores[id] = values

    def get(self):
        return self.__dict__
    
class ObjectDetection:
    def __init__(self, Id:Optional[str], Format:Optional[str], Confidence:Optional[float], ClassId:Optional[str] = None, ClassName:Optional[str]=None, BBox=None):
        self.Id = Id
        self.ClassId = ClassId
        self.ClassName = ClassName
        self.BBox = BBox
        self.Format = Format
        self.Confidence = Confidence

class VideoFrame:
    def __init__(self, frameId:Optional[str], timeOffsetMs:Optional[float], detections:ObjectDetection):
        self.frameId = frameId
        self.timeOffsetMs = timeOffsetMs
        self.detections = detections.__dict__.get('detections')

class ImageDetectionObject():
    def __init__(self):
        self.detections = list()
    
    def add(self, object_detection:ObjectDetection):
        self.detections.append(object_detection.__dict__)
    
    def get(self):
        return self.__dict__
    
class VideoDetectionObject():
    def __init__(self):
        self.frames = list()
    
    def add(self, video_frame:VideoFrame):
        self.frames.append(video_frame.__dict__)
    
    def get(self):
        return self.__dict__
    
class ImageClassificationElement():
    def __init__(self):
        self.confidence = dict()
    
    def add(self, key:str, value:(float, int)):
        assert isinstance(key, str) and key, "key is required and must be str."
        assert isinstance(value, (float, int)) and value is not None, "value is required and must be float or int."
        self.confidence[key]=value
    
    def get(self):
        return self.__dict__

class Embedding:
    def __init__(self, embedding: float):
        self.embedding = embedding

class ImageEmbedding:
    def __init__(self):
         self.embeddings = []

    def add(self, embedding_values: Embedding):
        self.embeddings.append(embedding_values.embedding)

    def get(self):
        return self.__dict__

class ROIEmbedding:
    def __init__(self):
         self.embeddings = dict()

    def add(self, id,  embedding_values: list):
        self.embeddings[id] = embedding_values

    def get(self):
        return self.__dict__
    