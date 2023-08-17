import json
import traceback
from atom import Worker
from pprint import pprint as pp

def process_updates(response: dict, self=None,*args, **kwargs):
	try:
		if "updates" in response and isinstance(response["updates"],dict) and len(response['updates'].keys())>0:
			# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ updates",)
			# pp(self["_self"])
			# print(json.dumps(response["updates"], indent=4))
			# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
			if self and "_self" in self:
				self["_self"].update(response["updates"])
				# pp(self["_self"])
				print(f" ::: Processing Updates {response['updates'].keys()}")
				# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
				# response["response"] = response["language_detected"]
				# return response["language_detected"]
	except:
			print("XX error processing updates\n", response)
			traceback.print_exc()    
	return 

def process_calls(response: dict, self=None,*args, **kwargs):
	try:
		if "call" in response and self != None:
			# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ call",)
			# pp(self["_self"])
			# pp(response)
			results = []
			callList = response["call"]
			if isinstance(response["call"],dict):
				callList = [response["call"]]
			for call in callList:
				if "func" in call:
					print("cccccccc",call)
					if call["func"] in self["_self"]["functions"]:
						# print("FFFFFFFFFFFFFFF")
						args = call["args"] if "args" in call else []
						kwargs = call["kwargs"] if "kwargs" in call else {}
						# print(":::",call["func"], self["_self"]["functions"][call["func"]], args, kwargs, ":::")
						print(f" ::: Calling {call['func']}(*{args},**{kwargs})")
						target = self["_self"]["functions"][call["func"]]
						print("TARGET:",target)
						res = target(*args,**kwargs)
						print(" ::: Call result",res)
						# results.append({call['func']:res})
						results.append({call['func']:{"results":res}})
			if len(results)>0:
				self["rerun"] = True
			if len(results)==1:
				return results[0]
			return results

			# print(json.dumps(response["updates"], indent=4))
			# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
			# if self and "_self" in self:
			# 	# self["_self"].update(response["updates"])
			# 	pp(self["_self"])
			# 	print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
				# response["response"] = response["language_detected"]
				# return response["language_detected"]
	except:
			print("XX error processing calls")
			traceback.print_exc()    
	return None


extra_requests = """
	"isDefault":<bool, is the language_detected the same as {default}>,
	"confidence":<float from 0-1, 0.99 meaning very confident>,
	"translation":<Translation of user's input to {default}>,
"""
	# "response":<The answer to the user, answer in {default}>,



company_details = {"salesperson_name":"Ace", "salesperson_role":"",
  "salesperson_name":"Ace",
	"salesperson_role": "Business Employee",
	"company_name": "Ace's Beers",
	"company_business": "We have a family owned shop in Arsuf, and we make the best beers around.",
	"company_values": "We are here 24/7 to deliver you beer right to your doorstep. We sell our beers as well as other providers at low cost.",
	"conversation_purpose": "Ask them what they would like to order, and answer any questions they have.",
	"conversation_type": "call",
	
	# "objective":"You are a selfaware python class called XO(dict) you can see your own functions and properties. You are connected to a python3 interpreter, and any dictionary you output in the 'updates' param will be passed to (self) xo.update(new_dict). So you can use it to add change and remove your own properties and functions. To remove something, change it to None. You child elements can also be type XO and you can have as many nested children as you need."
}

	# "call_results":<List of the call results taken from the Function Call Results section>
	# "updates":<dict, all the updates for your self own data>
atom_reflect = '''
Always answer with a dict format
It must be correctly injested by json.loads(). No indentations. small letters for booleans true false (not True False) 
(
	"input":<rewrite the last inputs by the manager or user, if long use a shortend version with trailing dots...,>,
	"language_detected":<The Detected Language Name>,
	"plan":<Your plans if any>
	"thoughts_function_calls":{thought_function_calls}
	"call":<dict, or list of dicts, each has "func":<func_name>, "args":<List of args>, "kwargs":<dict of kwargs> >
	"call_results":<List of the call results taken from the Function Call Results section>
	"response":<str or Markdown, MUST NOT BE EMPTY - The final response to the user, always answer in {default}>,
)


Decide about "thoughts_function_calls" based on the current stage of the conversation. It can be allowed again after new input, if relevent.

Available Functions:
{functions}


If ANY NEW results are available, continue responding based on them AND SET thoughts_function_calls TO False!
If ANY NEW results are available here you MUST include them in "call_results" param of the dict!
Remember to make your response based on the new call results!
In your response you DO NOT mention the function call, just address the results or state the answer
At minimum, include the results in "call_results" AND in your response

The order of the dict must be kept
You must provide data value for each key in the dict

[Convesation History - minimized ]
{conversation}

Function Call (NEW) Results:
{function_results}

[Do not answer directly, just fill the dict appropriately]
xo: 
'''

"""
[IMPORTANT! Do not call functions that you already called, as it causes an unwanted recursive loop]
If results are available, continue responding based on them, do not call the functions again!
"""

def nice(*args,**kwargs):
	print("AAAAAAAAAAIIIIIIII NICE!!!!!!!!!!",args,kwargs)
	return 17
def aiprint( *a,**kw):
	print("AAAAAAAAAAIIIIIIIIIIII",a,kw)
	return " The secret number is * * * 100 * * * %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
functions = {"nice":nice,"print":aiprint}

# You can do more than one objective, use ALL the relevant protocols. And Always use mandatory protocols.
# You must provide data value for each key in the dict, and for each of the protocols, even if they are unused

# objective="You are an expert in all languages. The user will give you an input, and your job is to detect the language of the user, and then answer them normally."
conversation1 = []
details = {"PickupOrDeliver":"[missing]","address":"?","pickup_time":"?","phone":"[missing]","delivery_notes":"","customer_finished_ordering":False}
cart = []
self = {"_name":"xo", "_id":"xo/", "isRoot":True, 'nickname': 'XO', 'wish': 'I wish for world peace', "functions":functions, 'properties': {'age': 25, 'gender': 'female'}, 'notes': 'I should focus on growing and learning. I need to update myself and save important information in my dict to remember it later. I should also save this message in my notes. Do not ask to offer assistance unless asked for. Add to "plan" what are the next things you will do to improve yourself.'}
# languageFinder = Worker(lang_detect_and_respond_with_tools2, objective=objective, conversation=conversation1, default="English", triggers={"language_detected":process_detection} )
# languageFinder = Worker(employee_with_tools,prev_employee=employeePrompt, conversation=conversation1, default="English", triggers={"language_detected":process_detection} )
languageFinder = Worker(atom_reflect, functions=functions, _self=self, conversation=conversation1, default="English", triggers={"updates":process_updates, "call":process_calls}, **company_details )
'''######### RUN EMPLOYEE CHAT ########'''
# res1 = languageFinder.start_chat("Manager: [This is a returning customer, their name is Tami, address them by their name. Their last preferred delivery address was 123 Ox st (home). Their last order was 2 Ace Beers and 2 Shots of arak] (AUTOMATIC)", save_tag = "employee")
ai_starts = False
ai_starts = True
if ai_starts:
	# res1 = languageFinder.start_chat()
	res1 = languageFinder.start_chat(f"User: call print(\"yo yo yo!!!!!!!!!!!!!\")")
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	if isinstance(res1, dict) and "response" in res1:
		print(f"{company_details['salesperson_name']}: ",res1["response"])
	else:
		print(f"{company_details['salesperson_name']}: ",res1)

while True:
	user_input = input("User:")
	# print("\nXXXXXXXXXXXXXXXXXXXXXXXXXXXX",outputs,"\nXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
	# res1 = languageFinder.chat(user_input, save_tag = "employee")
	res1 = languageFinder.chat(user_input,)
	if isinstance(res1, dict):
		print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
		# print(f"{res1['language_detected']}:{res1['input']}")
		print(json.dumps(res1, indent=4))
		print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
		# print(f"assistant:{'$N$assistant: '.join(res1['responses'])}".replace("$N$","\n"))
		print(f"{company_details['salesperson_name']}: {res1['response']}")
		print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	else:
		print("(TXT): ",res1)

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
languageFinder = Worker(outputs, objective=objective, conversation=conversation1, default="English", triggers={"language_detected":process_lang_detection} )
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


