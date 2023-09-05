import json
from langchain import PromptTemplate
from autopop import DDBUtilWrapper 
from autopop import GoogleUtilWrapper 

class AspectFactory:
    def __init__(self, llm=None, ddb_util=None, google_util=None, context=None, aspect=None):
        self.llm = llm
        self.aspect = aspect
        self.context = context
        self.gu = google_util
        
        # load data from DDB
        try:
            self.template = ddb_util.get_prompt_data(context=self.context, aspect=aspect)        
            self.prompt = self.template.get('prompt', 'No prompt provided.')
        except Exception as e:
            print(e)
        
    def get_prompt(self, use_prompt=False):
        if use_prompt: return self.prompt

        template = """{guidelines}

Setting: {setting}

Persona: {persona}

Tone: {tone}

Task: {task}

Form: {form}

Examples: {examples}

Do not hallucinate - use only the context provided.

Answer: """

        prompt_template = PromptTemplate(
            input_variables=["guidelines", "setting", "persona", "task", "tone", "form", "examples"],
            template=template
        )

        formatted_prompt = prompt_template.format(
            guidelines=self.template.get('guidelines', 'No guidelines provided.'),
            setting=self.template.get('setting', 'No setting provided.'),
            persona=self.template.get('persona', 'No persona provided.'),
            task=self.template.get('task', 'No task provided.'),
            tone=self.template.get('tone', 'No tone provided.'),
            form=self.template.get('form', 'No form provided.'),
            examples='\n'.join(self.template.get('examples', ['No examples provided.']))
        )
        self.prompt = formatted_prompt
        return formatted_prompt

    def query(self, use_prompt=False, max_retries=3):
        retries = 0
        while retries < max_retries:
            prompt = self.get_prompt(use_prompt=use_prompt)
            answer = self.llm.query(prompt).answer
            if answer.lower() != 'i cannot answer.': return answer
            retries += 1
        return answer

    def post_doc(self, destination=None, use_prompt=False):
        fields = [{'table':self.context, 'row': self.aspect}]
        self.gu.post_doc_data(fields=fields, dest=destination, data=self.query(use_prompt=use_prompt)) 

    def post_sheet_query(self, sheet=None, column='D', q=query):
        fields = [{'table':self.context, 'row': self.aspect}]
        self.gu.post_sheet_data(fields=fields, sheet=sheet, column=column, data=query) 

    def post_sheet(self, sheet=None, column='D', use_prompt=False):
        fields = [{'table':self.context, 'row': self.aspect}]
        self.gu.post_sheet_data(fields=fields, sheet=sheet, column=column, data=self.query(use_prompt=use_prompt)) 

    def __str__(self):
        return json.dumps(self.template)
        
####################################################################

# fix URL
class DDBPromptWrapper(AspectFactory):
    du = DDBUtilWrapper()
    gu = GoogleUtilWrapper()
    def __init__(self, llm=llm, ddb_util=du, google_util=gu, context=None, aspect=None):
        super().__init__(llm=llm, ddb_util=ddb_util, google_util=google_util, context=context, aspect=aspect)
