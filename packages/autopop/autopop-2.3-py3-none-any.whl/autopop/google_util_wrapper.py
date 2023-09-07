import time
import requests

def call_post_sheet(instance, sheet=None, column=None, use_prompt=False): 
    instance.post_sheet(sheet=sheet, column=column, use_prompt=use_prompt)    

class GoogleUtilWrapper:
    def __init__(self, p2_url=None, gdt_url=None, pdest=None, gdest=None):
        self.p2_url = p2_url
        self.gdt_url = gdt_url
        self.pdest = pdest
        self.gdest = gdest

    def get_data(self, ep='', fields=None):
        payload = {}
        payload["p2"] = self.p2_url
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