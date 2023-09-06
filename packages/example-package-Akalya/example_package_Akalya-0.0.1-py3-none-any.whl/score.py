import json
import os
from cloudpickle import cloudpickle
import argparse

parser = argparse.ArgumentParser()
parser.parse_args()
model_name = 'model.pkl'





def load_model(model_file_name=model_name):
    
    model_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(model_dir)
    if model_file_name in contents:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), model_file_name), "rb") as file:
            return cloudpickle.load(file)
    else:
        raise Exception('{0} is not found in model directory {1}'.format(model_file_name, model_dir))


def predict(data, model=load_model()):
    
    from pandas import read_json, DataFrame
    from io import StringIO
    data = read_json(StringIO(data)) if isinstance(data, str) else DataFrame.from_dict(data)
    pred = model.predict(data).tolist()
    return {'prediction': pred}