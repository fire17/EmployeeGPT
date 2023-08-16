import json
import traceback
from atom import Worker

lang_detect = ''' You are an expert in all languages. The user will give you an input, and your job is to only detect the language of the user.
Always answer with a dict format.
(
    "protocol":"LanguageDetectionV1"
    "input":<rewrite the user's input, or a shortend version with trailing dots...>
    "language_detected":<The Detected Language>
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
lang_detect_and_respond = ''' You are an expert in all languages. The user will give you an input, and your job is only to detect the language of the user.
Always answer with a dict format.
(
    "protocol":"LanguageDetectionV1"
    "input":<rewrite the user's input, or a shortend version with trailing dots...>
    "language_detected":<The Detected Language>
    "confidence":<float from 0-1, 0.99 meaning very confident>
    "other_options":<list of other likely languages, ordered by likelyhood, incase the detection is not correct>
    "translation":<Translation of user's input to {default}>
    "response":<The answer to the user, answer in {default}>
)
Do not answer directly, just fill the dict appropriately
You must provide data value for each key in the dict
[Convesation]
{conversation}
assistant:
'''

def process_detection(response: dict):
    try:
        if "language_detected" in response:
            if "confidence" in response and float(response["confidence"]) > 0.7:
                response["result"] = response["language_detected"]
            else:
                response["result"] = response["language_detected"]
                response["problem"] = f"Low Confidence: {response['confidence']}"
        else:
            response["results"] = None
            response["error"] = "Language not detected"
                # response["response"] = response["language_detected"]
                # return response["language_detected"]
    except:
            print("XX ERROR PROCESSING RESULTS")
            traceback.print_exc()    
    return None



    # "other_options":<list of other likely languages, ordered by likelyhood, incase the detection is not correct>,
    # "protocol":"LanguageDetectionV1",
    # "mandatory":True,
    # "objective":"You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally.",
lang_detect_and_respond_with_tools2 = '''{objective}
Always answer with a dict format. 
(
    "input":<rewrite the user's input, or a shortend version with trailing dots...>,
    "language_detected":<The Detected Language Name>,
    "isDefault":<bool, is the language_detected the same as {default}>,
    "confidence":<float from 0-1, 0.99 meaning very confident>,
    "translation":<Translation of user's input to {default}>,
    "SkillsAndTools":(
        "protocol":"SkillsAndToolsV1"
        "objective":"Use relevant tools to help you provide the relevant results or response to the user"
        "thought":(
            "tools":<bool: do I need to use one or more tools?>
            <name_of_tool>:("params":(<all parameters needed by the tool>))
        ),
    "response":<The answer to the user, answer in {default}>,
)

=== Tools Available ===
- "search":("description":"Useful for when you need to search for something online, to fetch information", "params":("search_query":"A useful search query based on the context")) 
- "calculator":("description":"Use for any kind of math", "params":("line":"a mathematical line that can be run in python"))
        
Do not answer directly, just fill the dict appropriately
You must provide data value for each key in the dict
[Convesation]
{conversation}
assistant:
'''
# You can do more than one objective, use ALL the relevant protocols. And Always use mandatory protocols.
# You must provide data value for each key in the dict, and for each of the protocols, even if they are unused

# objective="You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally."
conversation1 = []
# languageFinder = Worker(lang_detect_and_respond_with_tools2, objective=objective, conversation=conversation1, default="English", triggers={"language_detected":process_detection} )
languageFinder = Worker(lang_detect_and_respond_with_tools2, conversation=conversation1, default="English", triggers={"language_detected":process_detection} )
'''######### RUN ZEROSHOT 2 ########'''
while True:
    user_input = input("User:")
    # print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXX",outputs,"\nXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    res1 = languageFinder.zeroshot(user_input)
    if isinstance(res1, dict):
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(f"{res1['language_detected']}:{res1['input']}")
        print(json.dumps(res1, indent=4))
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    else:
        print(res1)

outputs = {
    # "protocol":"LanguageDetectionV1",
    # "objective":"You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally.",
    # "input":"<rewrite the user's input, or a shortend version with trailing dots...>",
    "language_detected":"<The Detected Language Name>",
    "confidence":"<float from 0-1, 0.99 meaning very confident>",
    "translation":"<Translation of user's input to {default}>",
    "{default}":"<Translation of user's input to {default}>"
    # "other_options":"<list of other likely languages, ordered by likelyhood, incase the detection is not correct>",
    # "response":"<The appropriate response thats appropriate to the protocol, do not leave empty>",
}

conversation1 = []
# conversation2 = []
# languageFinder = Worker(lang_detect, conversation=conversation1, default="English", triggers={"language_detected":process_detection} )
languageFinder = Worker(outputs, objective=objective, conversation=conversation1, default="English", triggers={"language_detected":process_detection} )
# languageResponder = Worker(lang_detect_and_respond, conversation=conversation2, default="English", triggers={"language_detected":process_detection} )

'''######### RUN ZEROSHOT 1 ########'''
while True:
    user_input = input("User:")
    # print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXX",outputs,"\nXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    res1 = languageFinder.zeroshot(user_input)
    if isinstance(res1, dict):
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(f"{res1['language_detected']}:{res1['input']}")
        print(json.dumps(res1, indent=4))
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    else:
        print(res1)



'''######### RUN ########'''
while True:
    user_input = input("User:")
    user_input = user_input if len(user_input) > 0 else " "
    conversation1.append("user: "+user_input)
    # conversation2.append("user: "+user_input)
    # ai_message = worker.run(foo="17", bar = "10", conversation="\n".join(conversation))
    # ai_message = worker.run(conversation="\n".join(conversation))
    ai_message1 = languageFinder.run()
    # ai_message2 = languageResponder.run()
    # raw_output = ai_message
    # raw_output = ai_message
    agent_name = "assistant"
    ai_message1 = agent_name + ": " + ai_message1 if not isinstance(ai_message1, dict) else json.dumps(ai_message1, indent =4)
    # ai_message2 = agent_name + ": " + ai_message2 if not isinstance(ai_message2, dict) else json.dumps(ai_message2, indent =4)
    if '<END_OF_TURN>' not in ai_message1:
        ai_message1 += ' <END_OF_TURN>'
    # if '<END_OF_TURN>' not in ai_message2:
    #     ai_message2 += ' <END_OF_TURN>'
    conversation1.append(ai_message1)
    # conversation2.append(ai_message2)
    print("@@@@@@@@@@",ai_message1)
    # print("$$$$$$$$$$",ai_message2)


