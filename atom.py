from pprint import pprint as pp
import traceback
from xo.redis import xoRedis

print("xxx")
xo = xoRedis("atom",host='ethical-monarch-46113.upstash.io',port=46113,password='7a984cbd2d4b408e8d84c4c44deea3c5',ssl=True)

from langchain import LLMChain, PromptTemplate
# from langchain.llms import BaseLLM
import os
 # import your OpenAI key (put in your .env file)
with open('.env','r') as f:
    env_file = f.readlines()
envs_dict = {key.strip("'") :value.strip("\n") for key, value in [(i.split('=')) for i in env_file]}
os.environ['OPENAI_API_KEY'] = envs_dict['OPENAI_API_KEY']

from langchain.chat_models import ChatOpenAI
print("xxx")
llm = ChatOpenAI(temperature=0.2)
print("xxx")



# class ModelWrapper:
#     def incomming(msg, *arg, **kwargs):
#         pass
#     def step(*args, **kwargs):
#         pass

# class Agent(ModelWrapper):
#     pass

# class Employee(Agent):
#     def __init__(self):
#         self.model = ModelWrapper() # Add openai/ others
    
#     def incomming(msg, step=True, *arg, **kwargs):
#         if step:
#             return self.step(*args, **kwargs)
#         return ""
#     def step(*args, **kwargs):
#         pass

# class Company(dict):
#     def __init__(self, name, *args, **kwargs):
#         '''load company'''
#         self.id = "id_"+name



from salesgpt.chains import employeePrompt as acePrompt
verbose = False
verbose = True
def getVariables(txt=''''''):
    return ["foo","bar","conversation"]
    return ["salesperson_name",
            "salesperson_role",
            "company_name",
            "company_business",
            "company_values",
            "conversation_purpose",
            "conversation_type",
            "conversation_history",]
# prompt = PromptTemplate(template=acePrompt, input_variables=getVariables(acePrompt),)
fooPrompt = ''' You are to anwswer if only one of the following options:
FOO, BAR or BAZ
say FOO if you the user sends you: {foo} or multiples of it
say BAR if you the user sends you: {bar} or multiples of it
say FOO BAR if what the user sends is both a multiple of {foo} and {bar}
say BAZ for any other input

Confirm

[Conversation History]:
{conversation}
assitant:
'''
jsonPrompt = ''' You are to only anwswer with a dict format
take the user's input and turn it into a well formatted dictionary with all the details
(
    "protocol":"DictResponseV1"
    "user_request": [what the user wants]
    "thoughts":(
        tools:("Q":"Do I need to use Tools?", "A": "No")
        )
    "current_stage":[current stage in convestation]
    "export":(
        "key":[all key details from the user input, can be nested dict]
    )
    "response_to_user":[Always Provide Your final response]
)

[Conversation History]:
{conversation}
assitant:
'''

import re

def extract_named_parameters(s):
    pattern = r'\{([^}]+)\}'
    matches = re.findall(pattern, s)
    return matches
def extract_named_parameters2(s):
    pattern = r'\(([^}]+)\)'
    matches = re.findall(pattern, s)
    return matches
def extract_named_parameters3(s):
    pattern = r'\{([^{}]+)\}'
    matches = re.findall(pattern, s)
    return matches

def dynamicPrompt(prompt):
    params = extract_named_parameters3(prompt)
    # print("DDD params:",params)
    return PromptTemplate(template=prompt, input_variables=params,), params


import json
# prompt = PromptTemplate(template=fooPrompt, input_variables=getVariables(fooPrompt),)
# prompt = PromptTemplate(template=fooPrompt, input_variables=getVariables(fooPrompt),)
# conversation = ["assistant: Confirmed."]
# worker = makeWorker(jsonPrompt)
import re

class Worker(dict):
    def __init__(self, template,*args, **kwargs):
        self["objective"]="You are the most Capable Expert in any field, and you can determin the objective based on the structure of provided by the system below."
        for key in kwargs:
            self[key] = kwargs[key]
        self["function_results"] = []
        # self["function_calls_org"] = "<bool, Do I need to call a function? DO NOT USE if History shows you just called that function>"
        self["thought_function_calls_org"] = "<bool, Do I need to call a function? small letters for json>"
        self["thought_function_calls"] = self["thought_function_calls_org"]
        if isinstance(template, dict):
            start_d = {"input":"<rewrite the user's input, or a shortend version with trailing dots...>",}
            final_d = {**start_d, **template, **{"response":"<The appropriate response thats appropriate to the protocol, do not leave empty>",}}
            primer1 = """{objective}
Always answer with a dict format.            
"""         
            # outputs_primer = (json.dumps(final_d, indent=4)+"\n").replace("{","(").replace("}",")")
            dict_prompt = json.dumps(final_d, indent=4)+"\n"
            # dict_prompt = dict_prompt.replace("{","(").replace("}",")")
            params = extract_named_parameters3(dict_prompt)
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            # print(dict_prompt)
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            # print("params:",params)
            outputs_primer = dict_prompt#.replace("{","%(%").replace("}","%)%")
            for param in params:
                if param in self and "{"+param+"}" in outputs_primer:
                    # print("INJECTING:",param, self[param])
                    outputs_primer = outputs_primer.replace("{"+param+"}", self[param])
            # outputs_primer = (json.dumps(final_d, indent=4)+"\n").replace("%(%","(").replace("%)%",")")
            outputs_primer = outputs_primer.replace("{","(").replace("}",")")

            closer='''Do not answer directly, just fill the dict appropriately
You must provide data value for each key in the dict
[Convesation]
{conversation}
{salesperson_name}:'''
            template = primer1+outputs_primer+closer

        def makeWorker(promptTemplate):
            prompt, params = dynamicPrompt(promptTemplate)
            worker = LLMChain(prompt=prompt,llm=llm, verbose=verbose)
            return worker, params
        _worker, _params = makeWorker(template)
        self["_worker"] = _worker
        self["_params"] = _params

    
    def start_chat(self,incoming=None, save_tag=None, *args, **kwargs):
        if incoming != None:
            incoming = incoming if len(incoming) > 0 else " "
            self["conversation"].append(incoming)
        ai_message = self.run()
        # self["conversation"].pop()
        raw_output = ai_message
        agent_name = "{salesperson_name}"
        if save_tag != None and isinstance(ai_message,dict):
            ai_message = {f"{save_tag}":ai_message[save_tag]}
        ai_message_record = agent_name + ": " + ai_message if not isinstance(ai_message, dict) else agent_name + ": " +json.dumps(ai_message)
        # if '<END_OF_TURN>' not in ai_message_record:
        #     ai_message_record += ' <END_OF_TURN>'
        self["conversation"].append(ai_message_record)
        # print("@@@@@@@@@@",ai_message_record)
        # print("########## ai_message:",type(ai_message))
        # print("XXXXXXXXXXXXXxx")
        # print(raw_output)
        # print("XXXXXXXXXXXXXxx")
        if isinstance(ai_message, dict):
            if "response" in ai_message:
                pass # print("$$$$$$$$$", ai_message["response"])
            if "responses" in ai_message:
                pass #  print("$$$$$$$$$", ai_message["responses"])
            return raw_output
        '''maybe retry a couple of times...?'''
        return ai_message_record


    
    def chat(self, incoming, save_tag = None, *args, **kwargs):
        incoming = incoming if len(incoming) > 0 else " "
        self["conversation"].append("User: "+incoming)
        ai_message = self.run()
        # self["conversation"].pop()
        raw_output = ai_message
        agent_name = "{salesperson_name}"
        if save_tag != None and isinstance(ai_message,dict):
            ai_message = {f"{save_tag}":ai_message[save_tag]}
        ai_message_record = agent_name + ": " + ai_message if not isinstance(ai_message, dict) else agent_name + ": " +json.dumps(ai_message)
        # if '<END_OF_TURN>' not in ai_message_record:
        #     ai_message_record += ' <END_OF_TURN>'
        self["conversation"].append(ai_message_record)
        # print("@@@@@@@@@@ on record:",ai_message_record)
        # print("########## ai_message:",type(ai_message))
        # print("XXXXXXXXXXXXXxx")
        # print(raw_output)
        # print("XXXXXXXXXXXXXxx")
        if isinstance(ai_message, dict):
            if "response" in ai_message:
                pass # print("$$$$$$$$$", ai_message["response"])
            if "responses" in ai_message:
                pass # print("$$$$$$$$$", ai_message["responses"])
            return raw_output
        '''maybe retry a couple of times...?'''
        return ai_message_record 
        # ai_message = worker.run(foo="17", bar = "10", conversation="\n".join(conversation))
        # ai_message = worker.run(conversation="\n".join(conversation))

    def zeroshot(self, incoming, *args, **kwargs):
        incoming = incoming if len(incoming) > 0 else " "
        self["conversation"].append("User: "+incoming)
        ai_message = self.run()
        self["conversation"].pop()
        if isinstance(ai_message, dict):
            return ai_message
        '''maybe retry a couple of times...?'''
        return ai_message 
        # ai_message = worker.run(foo="17", bar = "10", conversation="\n".join(conversation))
        # ai_message = worker.run(conversation="\n".join(conversation))
        raw_output = ai_message
        agent_name = "assistant"
        ai_message = agent_name + ": " + ai_message if not isinstance(ai_message, dict) else json.dumps(ai_message, indent =4)
        if '<END_OF_TURN>' not in ai_message:
            ai_message += ' <END_OF_TURN>'
        conversation.append(ai_message)
        print("@@@@@@@@@@",ai_message)

    def run(self, can_trigger = True, iteration = 0):
        prep_params = {}
        def process_param(p, v):
            if "conversation" == p:
                return "\n".join(v)
            return v
        for p in self["_params"]:
            prep_params[p] = "{"+p+"}" if p not in self else process_param(p, self[p])
        res = self["_worker"].run(**prep_params)
        try:
            # resDict = d
            # str_dict = '{"key1": "value1", "key2": "value2", "key3": "value3"}'
            # clean_res = "\n".join((t.strip() for t in res.split("\n")))
            # clean_res = "\n".join((t.strip() for t in res.split("\n")))
            normal_dict = {}
            experiment = False
            if experiment:
                clean_res = re.sub(r'[^\x20-\x7E]', '', res).strip()

                c, tries, stop = 0, 3, False
                
                while c <= tries and not stop:
                    c+=1
                    if c==tries:
                        normal_dict = json.loads(res.strip())
                        stop = True
                    else:
                        try:
                            normal_dict = json.loads(clean_res)
                            stop = True
                        except:
                            print("XXXXXXX json error",)
            else:
                # normal_dict = json.loads(str(res).strip())
                x = "$$$"+res.strip().replace("\n","")+"$$$"
                # print(x)
                normal_dict = json.loads(x.strip("$$$").replace("<END_OF_TURN>",""))
# json.loads(data.decode("utf-8"))
            # print("&&&&&&&&&&&&&&&&&&&")
            # print("&&&&&&&&&&&&&&&&&&&")
            # print("&&&&&&&&&&&&&&&&&&&",normal_dict["thoughts_function_calls"] if "thoughts_function_calls" in normal_dict else "XXX")
            # print("&&&&&&&&&&&&&&&&&&&")
            # pp(normal_dict)
            if "triggers" in self and can_trigger and (iteration==0 or "thoughts_function_calls" in normal_dict and normal_dict["thoughts_function_calls"]==True):
                for key in self["triggers"]:
                    if key in normal_dict:
            # if "triggers" in self:
            #     for section in self["triggers"]:
            #         if section in self["triggers"]:
            #             for key in self["triggers"][section]:
            #                 if key in normal_dict[section]:
                        # print("FOUND TRIGGER!!!!!", key)
                        # trigger_res = self["triggers"][section][key](normal_dict[section])
                        trigger_res = self["triggers"][key](normal_dict, self=self)
                        if not isinstance(trigger_res,list):
                            trigger_res = [trigger_res]
                        if trigger_res != None:
                            # print("CONVERTED!!!!!!!!!!!", normal_dict)

                            ''' # Call worker again if needed'''
                            if "rerun" in self and self["rerun"]:
                                self["rerun"] = False
                                self["conversation"].append("Ace: "+str(normal_dict))
                                for func_result in trigger_res:
                                    self["function_results"].append(func_result)
                                    
                                    func = list(func_result.keys())[0]
                                    # results = func_result["results"]
                                    self["conversation"].append(f"[ Ace Called Function \"{func}\" Successfully - USE THE NEW RESULTS IN YOUR NEXT RESPONSE! ]")
                                    # self["conversation"].append(f"[DO NOT RECALL {func}]")
                                # self["conversation"].append(f"")
                                '''place results in normal_dict for history record'''
                                # pp(normal_dict)
                                print("11111111111111111111")
                                print("11111111111111111111")
                                print("11111111111111111111")
                                nextRun = self.run(can_trigger=True, iteration = iteration+1)
                                print("%%%%%%%%%%%% NEXT RUN %%%%%%%%%%%%%%%%")
                                pp(nextRun)
                                print("%%%%%%%%%%%% END NEXT RUN %%%%%%%%%%%%%%%%")
                                pp(normal_dict)
                                print("%%%%%%%%%%%% END ORIGINAL %%%%%%%%%%%%%%%%")
                                self["function_results"].clear()
                                self["conversation"].pop()
                                self["conversation"].pop()
                                # self["conversation"].pop()

                                return nextRun
                            
                            # return trigger_res
                        
                        # if section in normal_dict and "response" in normal_dict[section] and normal_dict[section]["response"] != None:
                        if "response" in normal_dict and normal_dict["response"] != None:
                            # print(normal_dict[section]["response"])
                            # print(normal_dict["response"])
                            pass
                        # return normal_dict
            else:
                print("2222222222222222222")
                print("2222222222222222222")
                print("2222222222222222222")

            if "final_process" in self:
                self["final_process"](normal_dict, self=self)
            # print("CONVERTED!!!!!!!!!!!", normal_dict)
            return normal_dict
        except:
            print("XX ERROR CONVERTING TO DICT")
            traceback.print_exc()
        return res

if False:
    conversation = []

    lang_detect = '''
    Always answer with a dict format.
    (
        "protocol":"LanguageDetectionV1"
        "objective":"You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally."
        "input":<rewrite the user's input, or a shortend version with trailing dots...>
        "language_detected":<The Detected Language (use full name ie "English" not "en")>
        "confidence":<float from 0-1, 0.99 meaning very confident>
        "other_options":<list of other likely languages, ordered by likelyhood, incase the detection is not correct>
        "response":<The appropriate response thats appropriate to the protocol, do not leave empty>
    )
    Do not answer directly, just fill the dict appropriately
    You must provide data value for each key in the dict
    [Convesation]
    {conversation}
    assistant:
    '''

    # primer1 = """Always answer with a dict format.
    # """
    objective="You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally."
    outputs = {
        # "protocol":"LanguageDetectionV1",
        # "objective":"You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally.",
        # "input":"<rewrite the user's input, or a shortend version with trailing dots...>",
        "language_detected":"<The Detected Language Name>",
        "confidence":"<float from 0-1, 0.99 meaning very confident>",
        "translation":"<Translation of user's input to {default}>"
        # "other_options":"<list of other likely languages, ordered by likelyhood, incase the detection is not correct>",
        # "response":"<The appropriate response thats appropriate to the protocol, do not leave empty>",
    }
    # outputs_primer = (json.dumps(outputs, indent=4)+"\n").replace("{","(").replace("}",")")
    # closer='''Do not answer directly, just fill the dict appropriately
    # You must provide data value for each key in the dict
    # [Convesation]
    # {conversation}
    # assistant:'''
    # lang_detect = primer1+outputs_primer+closer
    from atom_prompts import process_detection


    # from lang_detect import lang_detect, lang_detect_and_respond, process_detection

    # languageFinder = Worker(lang_detect_and_respond_with_tools, conversation=conversation, default="English", triggers={"LanguageDetection":{"language_detected":process_detection}} )
    # languageFinder = Worker(lang_detect, conversation=conversation, default="English", triggers={"language_detected":process_detection} )
    # languageFinder = Worker(outputs, objective=objective, conversation=conversation, default="English", triggers={"language_detected":process_detection} )
    languageFinder = Worker(outputs, objective=objective, conversation=conversation, default="English")#, triggers={"language_detected":process_detection} )

    # return
    '''######### RUN ########'''
    while True:
        user_input = input("User:")
        res1 = languageFinder.zeroshot(user_input)
        print(f"{res1['language_detected']}:{res1['input']}")


    # worker = Worker(jsonPrompt, conversation=conversation)
    worker = languageFinder



    '''######### RUN ########'''
    while True:
        user_input = input("User:")
        user_input = user_input if len(user_input) > 0 else " "
        conversation.append("user: "+user_input)
        # ai_message = worker.run(foo="17", bar = "10", conversation="\n".join(conversation))
        # ai_message = worker.run(conversation="\n".join(conversation))
        ai_message = worker.run()
        raw_output = ai_message
        agent_name = "assistant"
        ai_message = agent_name + ": " + ai_message if not isinstance(ai_message, dict) else json.dumps(ai_message, indent =4)
        if '<END_OF_TURN>' not in ai_message:
            ai_message += ' <END_OF_TURN>'
        conversation.append(ai_message)
        print("@@@@@@@@@@",ai_message)

    # ai_message = worker.run(
    #                 conversation_stage=self.current_conversation_stage,
                    # conversation_history="\n".join(self.conversation_history),
    #                 salesperson_name=self.salesperson_name,
    #                 salesperson_role=self.salesperson_role,
    #                 company_name=self.company_name,
    #                 company_business=self.company_business,
    #                 company_values=self.company_values,
    #                 conversation_purpose=self.conversation_purpose,
    #                 conversation_type=self.conversation_type,
    #             )

    # Add agent's response to conversation history
    #TODO: check for <EVENTS> in ai_message + add them to ai_message / conversation_history
    # self.conversation_history.append(ai_message)
    # SalesGPT.pretty(ai_message.replace("<END_OF_TURN>", ""))
    #TODO: Send results back to client, after event filter, 
    # return ai_message



    if __name__ == "__main__":

        company_name = "Ace's Beers"

        agent = Employee()
        company = Company(company_name)
        '''connect to telegram / whatsapp'''
        if xo.companies[company.id] != True:
            xo.companies[company.id] = True

