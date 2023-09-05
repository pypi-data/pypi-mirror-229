import os
import boto3
import openai
from paperqa import Docs
from urllib.parse import urlparse
from langchain.chat_models import ChatAnthropic, ChatOpenAI

def initialize_llm(documents, temperature=0.7,
                   openai_api_key=os.environ['OPENAI_API_KEY'], 
                   anthropic_api_keyos.environ['ANTHROPIC_API_KEY']):
    # Initialize the language models
    gpt4 = ChatOpenAI(model='gpt-4', temperature=temperature, openai_api_key=openai_api_key)
    claude = ChatAnthropic(model="claude-2", temperature=temperature, anthropic_api_key=anthropic_api_key)
    llm = Docs(llm=gpt4, summary_llm=claude)

    # Add documents to Paper QA
    for path in documents:
        parsed_url = urlparse(path)
        scheme = parsed_url.scheme
        ext = os.path.splitext(path)[-1].lower()

        if scheme in ['http', 'https']:
            # If it's a web URL, use add_url
            llm.add_url(path)
        elif scheme == 's3':
            # If it's an S3 URL, download the file first
            s3 = boto3.client('s3')
            bucket = parsed_url.netloc
            key = parsed_url.path.lstrip('/')
            local_path = f"/tmp/{os.path.basename(key)}"
            s3.download_file(bucket, key, local_path)

            # Then add it based on its extension
            if ext == '.pdf':
                llm.add(local_path)
            else:
                with open(local_path, 'r') as f:
                    text_content = f.read()
                    llm.add_file(f, text_content)
        else:
            # If it's a local file, add it based on its extension
            if ext == '.pdf':
                llm.add(path)
            else:
                with open(path, 'r') as f:
                    text_content = f.read()
                    llm.add_file(f, text_content)
    
    return llm
