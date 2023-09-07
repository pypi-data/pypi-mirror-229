import requests

class DDBUtilWrapper:
    def __init__(self, ddb_url=None):
        self.ddb_url = ddb_url

    def get_prompt_data(self, context=None, aspect=None, attributes=[]):
        payload = {}
        payload["attributes"] = attributes
        if aspect: payload["aspect"] = aspect
        if context: payload["context"] = context
        response = requests.get(self.ddb_url, json=payload)
        if response.status_code == 200: return response.json()
        else: return f"Request failed with status code: {response.status_code}"

    def post_prompt_data(self, context=None, **kwargs):
        class Aspect:
            def __init__(self, **kwargs):
                self.expected_keys = ['name', 'task', 'form', 'examples', 'setting', 'persona', 'prompt', 'guidance']
                
                # Initialize all accepted attributes to None
                for key in self.expected_keys:
                    setattr(self, key, None)
                    
                # Filter out unrecognized keys from kwargs and set attributes
                _ = [setattr(self, k, v) for k, v in kwargs.items() if k in self.expected_keys]
                
            def data(self):
                return {key: getattr(self, key) for key in self.expected_keys if getattr(self, key, None) is not None}

        aspect = Aspect(**kwargs)
        payload = {}
        payload["context"] = context
        payload["aspect"] = aspect.data()
        response = requests.post(self.ddb_url, json=payload)
