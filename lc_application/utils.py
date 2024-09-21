# utils.py

import os
import json

DEPLOYMENT_ID_FILE = 'deployment_id.json'

def get_deployment_id():
    if os.path.exists(DEPLOYMENT_ID_FILE):
        with open(DEPLOYMENT_ID_FILE, 'r') as file:
            data = json.load(file)
            return data.get('deployment_id')
    return None

def save_deployment_id(deployment_id):

    with open(DEPLOYMENT_ID_FILE, 'w') as file:
        json.dump({'deployment_id': deployment_id}, file)
