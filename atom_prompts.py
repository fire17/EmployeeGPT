
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
lang_detect_and_respond = ''' You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally.
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

lang_detect_and_respond_with_tools = '''
Always answer with a dict format. 
"LanguageDetection":(
    "protocol":"LanguageDetectionV1"
    "mandatory":True
    "objective":"You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally."
    "input":<rewrite the user's input, or a shortend version with trailing dots...>
    "language_detected":<The Detected Language Name>
    "confidence":<float from 0-1, 0.99 meaning very confident>
    "other_options":<list of other likely languages, ordered by likelyhood, incase the detection is not correct>
    "translation":<Translation of user's input to {default}>
    "response":<The answer to the user, answer in {default}>
),
"SkillsAndTools":(
    "protocol":"SkillsAndToolsV1"
    "objective":"Use relevant tools to help you provide the relevant results or response to the user"
    "thought":(
        "tools":<bool: do I need to use one or more tools?>
        <name_of_tool>:("params":(<all parameters needed by the tool>))
    ),
    "tools_available":( # Can ommit if thought["tools"] == False
        "search":("description":"Useful for when you need to search for something online, to fetch information", "params":("search_query":"A useful search query based on the context")) 
        "calculator":("description":"Use for any kind of math", "params":("line":"a mathematical line that can be run in python"))
    )
)
Do not answer directly, just fill the dict appropriately
You can do more than one objective, use ALL the relevant protocols. And Always use mandatory protocols.
You must provide data value for each key in the dict, and for each of the protocols, even if they are unused
[Convesation]
{conversation}
assistant:
'''