import time
import json
import boto3
import requests
from urllib.parse import urlparse

def call_post_sheet(instance, sheet=None, column=None, use_prompt=False): 
    instance.post_sheet(sheet=sheet, column=column, use_prompt=use_prompt)    

def get_bsme_interview(self):
    return gu.get_data('bsme')

def get_tsme_interview(self):
    return gu.get_data('tsme')

def get_related_docs(gu, s3_path):
    s3 = boto3.client('s3')
    parsed_url = urlparse(s3_path)
    s3_bucket = parsed_url.netloc
    s3_directory = parsed_url.path.lstrip('/')
    filenames = []

    for k, v in gu.get_data('related').items():
        data = json.dumps(gu.get_data(p2_url=v))
        s3_key = f"{s3_directory}{k}.json" 
        s3.put_object(Body=data, Bucket=s3_bucket, Key=s3_key)
        filenames.append(s3_key)
    return filenames

def get_related_docs(gu, s3_path):
    s3 = boto3.client('s3')
    parsed_url = urlparse(s3_path)
    s3_bucket = parsed_url.netloc
    s3_directory = parsed_url.path.lstrip('/')
        
    for k, v in gu.get_data('related').items():
        data = gu.get_data(p2_url=p2 + url)        
        s3_key = f"{s3_directory}/{k}.json"  # Assuming the data is JSON
        s3.put_object(Body=data_str, Bucket=s3_bucket, Key=s3_key)

class GoogleUtilWrapper:
    def __init__(self, p2_url=None, gdt_url=None, pdest=None, gdest=None):
        self.p2_url = p2_url
        self.gdt_url = gdt_url
        self.pdest = pdest
        self.gdest = gdest

    def get_data(self, ep='', fields=None, p2_url=None):
        payload = {}
        payload["p2"] = self.p2_url if not p2_url else p2_url
        if fields: payload["fields"] = fields
        response = requests.get(self.gdt_url + ep, json=payload)
        return response.json()

    def post_doc_data(self, fields=[], data=None):
        payload = {}
        payload["p2"] = self.p2_url
        payload["fields"] = fields
        payload["destination"] = self.pdest
        if data: payload["data"] = data
        response = requests.post(self.gdt_url, json=payload)

    def post_sheet_data(self, fields=[], aspects=[], sheet=None, column=None, data=None):
        if aspects:
            fields = [{"table": aspect['table'], "row": row} for aspect in aspects for row in aspect['row']]
        payload = {}
        payload["p2"] = self.p2_url
        payload["fields"] = fields
        payload["destination"] = self.gdest
        if data: payload["data"] = data
        if sheet: payload["sheet"] = sheet
        if column: payload["source"] = column
        response = requests.post(self.gdt_url, json=payload)