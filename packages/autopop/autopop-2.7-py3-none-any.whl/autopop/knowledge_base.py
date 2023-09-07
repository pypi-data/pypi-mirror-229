import os
import boto3
from urllib.parse import urlparse
from paperqa import Docs, Text, Doc  
from langchain.chat_models import ChatAnthropic, ChatOpenAI

def knowledge_base(documents, temperature=0.7, is_text=False):
    # Initialize the language models
    gpt4 = ChatOpenAI(model='gpt-4', temperature=temperature)
    claude = ChatAnthropic(model="claude-2", temperature=temperature)
    
    llm_openai = Docs(llm=gpt4)
    llm_claude = Docs(llm=claude)
    llm_combo = Docs(llm=gpt4, summary_llm=claude)

    llms = {'gpt4': llm_openai, 'claude': llm_claude, 'combo': llm_combo}

    if is_text:
        doc = Doc(docname="MyTextDoc", citation="My Citation", dockey="MyDocKey")
        text = Text(text=documents, name="MyTextName", doc=doc)
        for llm in llms.values():
            llm.add_texts([text], doc)
        return llms
    
    s3 = boto3.client('s3')

    for path in documents:
        parsed_url = urlparse(path)
        scheme = parsed_url.scheme
        ext = os.path.splitext(path)[-1].lower()

        if scheme == 's3':
            bucket = parsed_url.netloc
            key = parsed_url.path.lstrip('/')

            if key.endswith('/'):  # It's a directory
                objects = s3.list_objects(Bucket=bucket, Prefix=key)
                for obj in objects.get('Contents', []):
                    file_key = obj['Key']
                    local_filename = os.path.basename(file_key)
                    if local_filename:
                        local_path = f"/tmp/{local_filename}"
                        s3.download_file(bucket, file_key, local_path)
                        for llm in llms.values():
                            llm.add(local_path)
            else:  # It's a file
                local_path = f"/tmp/{os.path.basename(key)}"
                s3.download_file(bucket, key, local_path)
                for llm in llms.values():
                    llm.add(local_path)

        elif scheme in ['http', 'https']:
            for llm in llms.values():
                llm.add_url(path)
        else:
            if ext == '.pdf':
                for llm in llms.values():
                    llm.add(path)
            else:
                with open(path, 'r') as f:
                    text_content = f.read()
                    for llm in llms.values():
                        llm.add_file(f, text_content)
    return llms