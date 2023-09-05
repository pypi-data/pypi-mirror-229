import time
import requests
from urllib.parse import urljoin
from selenium import webdriver

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

    def post_sheet_data(self, fields=[], sheet=None, column=None, data=None):
        payload = {}
        payload["p2"] = self.p2_url
        payload["fields"] = fields
        payload["destination"] = self.gdest
        if data: payload["data"] = data
        if sheet: payload["sheet"] = sheet
        if column: payload["source"] = column
        response = requests.post(self.gdt_url, json=payload)
        
    def get_recording_data(self, interview_type=None, max_attempts=20, sleep_interval=1, return_url=True):
        url = self.get_data(interview_type)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Browse to the target website
        driver.get(url)
        
        # Inject JavaScript to monitor XHR responses
        script = '''
        (function() {
            var open = window.XMLHttpRequest.prototype.open;
            window.responses = [];
            window.XMLHttpRequest.prototype.open = function(method, url) {
                this.addEventListener('load', function() {
                    if(this.responseText.startsWith('WEBVTT')) {
                        window.responses.push({content: this.responseText, url: url});
                    }
                });
                open.apply(this, arguments);
            };
        })();
        '''
        driver.execute_script(script)
        
        # Poll for captured responses
        attempts = 0
        webvtt_content = None
        webvtt_url = None
        while attempts < max_attempts:
            webvtt_responses = driver.execute_script('return window.responses')
            if webvtt_responses:
                webvtt_content = webvtt_responses[0]['content']
                webvtt_url = webvtt_responses[0]['url']
                break
            time.sleep(sleep_interval)
            attempts += 1
        
        driver.quit()
        
        if return_url:
            # Append the TLD from the request to the resultant URL
            full_url = urljoin(url, webvtt_url)
            return full_url
        else:
            return webvtt_content 
