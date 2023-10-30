import argparse

import os
import json
import time

from salesgpt.agents import SalesGPT, Tool_master
from langchain.chat_models import ChatOpenAI


from xo.redis import xoRedis

# xo = xoRedis("test.engineergpt")
# xo = xoRedis("test.engineergpt", host='wise-coyote-46085.upstash.io', port=46085, password='7fdf57fde49e4eadb7a260d0e38230a2', ssl=True )
xo = xoRedis("test.engineergpt",host='ethical-monarch-46113.upstash.io',port=46113,password='7a984cbd2d4b408e8d84c4c44deea3c5',ssl=True)
# Tool_master = False   
debug_master=False

def processAIStep(msg, agent:SalesGPT):
    if debug_master:print(" ::: Processing Events")
    # print(msg)
    event_detected = "<STAGE" in msg.split("\n")[0]
    if event_detected:
        event = ":".join(msg.split("\n")[0].split(":")[1:])
        if debug_master:print("$"*10)
        stage_id = event.split(":")[1].split("-")[0].strip()
        stage_name = event.split("-")[1].split(">")[0].strip()
        if debug_master:print(f"Stage {stage_id} - {stage_name}")
        if debug_master:print("$"*10)
        
        def welcome_returning(manager_msg="[This is a returning customer, their name is Tami, address them by their name. Their last preferred delivery address was 123 Ox st (home). Their last order was 2 Ace Beers and 2 Shots of arak] (AUTOMATIC)",*a, **kw):
            if debug_master:print(" @@@ Adding Returning Client's Info @@@ !!!!!!!!! (AUTOMATIC)")
            # print(manager_msg)
            print("\033[90m" + manager_msg + "\033[0m")
            # xo.step.manager = "[This is a returning customer, his last delivery address was 123 Ox st]"
            # agent.manager_step("<STAGE-0:init>")
            agent.manager_step(manager_msg)
        def send_bon(manager_msg = "[Sending payment link to customer] (AUTOMATIC)",
                     manager_msg2 = "[*Payment Successful*] (AUTOMATIC)", *a, **kw):
            
            line = " @@@ GENERATING & SENDING BON @@@"
            print("\033[92m" + line + "\033[0m")
            print("\033[92m" + manager_msg + "\033[0m")
            print("\033[92m" + manager_msg2 + "\033[0m")
            # print(manager_msg)
            # print(manager_msg2)
            # xo.step.manager = "[PAYMENT LINK SENT TO CLIENT !!!!!!!!! (AUTOMATIC) ] "
            agent.manager_step(manager_msg)
            agent.manager_step(manager_msg2)
            print("\033[90m" + "[Continue]" + "\033[0m")
            agent.step()
        # print("::::::::::::: SUBS:",xo.step.manager._subscribers)
        def await_manager():
            print("\033[90m" + "[Awaiting Managers to Approve The Order]" + "\033[0m")

    
        def add_to_cart(*args, **kwargs):
            line = " @@@ UPDATING CART @@@ "
            print("\033[92m" + line + "\033[0m")

        
        triggered_events = {"0":welcome_returning,"2":add_to_cart,"3":send_bon, "5":await_manager}
        if stage_id in triggered_events:
            triggered_events[stage_id]()
        else:
            if debug_master:print(f"----------STAGE{stage_id} not in {triggered_events}")
   

if __name__ == "__main__":

    # import your OpenAI key (put in your .env file)
    with open('.env','r') as f:
        env_file = f.readlines()
    envs_dict = {key.strip("'") :value.strip("\n") for key, value in [(i.split('=')) for i in env_file]}
    os.environ['OPENAI_API_KEY'] = envs_dict['OPENAI_API_KEY']

    # Initialize argparse
    parser = argparse.ArgumentParser(description='Description of your program')

    # Add arguments
    parser.add_argument('--config', type=str, help='Path to agent config file', default='')
    parser.add_argument('--verbose', type=bool, help='Verbosity', default=False)
    parser.add_argument('--max_num_turns', type=int, help='Maximum number of turns in the sales conversation', default=20)

    # Parse arguments
    args = parser.parse_args()

    # Access arguments
    config_path = args.config
    verbose = args.verbose
    max_num_turns = args.max_num_turns

    llm = ChatOpenAI(temperature=0.2)
    
    if config_path=='':
        print('No agent config specified, using a standard config')
        USE_TOOLS=False
        if USE_TOOLS:
            sales_agent = SalesGPT.from_llm(llm, use_tools=True, 
                                    menu = "menu.txt",
                                    salesperson_name="Ted Lasso",
                                    verbose=verbose)
        else:
            print("---BON EMPLOYEE---")
            sales_agent = SalesGPT.from_llm(llm, use_tools=Tool_master, verbose=verbose, menu = "menu.txt",)
    else:
        with open(config_path,'r') as f:
            config = json.load(f)
        print(f'Agent config {config}')
        sales_agent = SalesGPT.from_llm(llm, verbose=verbose, **config)


    sales_agent.seed_agent()

    def takeStep(human_input, role="manager"):
        print("\033[90m" + f"[{role}:{human_input}]" + "\033[0m")
        if role == "manager":
            sales_agent.manager_step(human_input)
        if role == "user":
            sales_agent.human_step(human_input)
        if role == "agent":
            sales_agent.step()

    
    def stepWrapper(i,*a, **kw):
        role="manager" if "role" not in kw else kw["role"]
        if debug_master: print("@@@@@@@@@@@@@@ STEPPING @@@@@@@@@@@@@@", i,":", a,":", kw)
        if i != None and i!=-1:
            return takeStep(i, role=role)
        return None

    xo.step = -1
    xo.step.manager = -1
    xo.step.user = -1
    xo.step.agent = -1
    # time.sleep(1)
    # def resetTriggers(xobj, triggers = ["manager","user","agent"]):
    #     for t in triggers:
    #         xobj[t] = -1
    # resetTriggers(xo.step)
    
    xo.step._subscribers.clear()
    xo.step.manager._subscribers.clear()
    xo.step.user._subscribers.clear()
    xo.step.agent._subscribers.clear()
    xo.step @= lambda x, *a, **kw: stepWrapper(x,role="manager",*a,**kw)
    xo.step.manager @= lambda x, *a, **kw: stepWrapper(x,role="manager",*a,**kw)
    xo.step.user @= lambda x, *a, **kw: stepWrapper(x,role="user",*a,**kw)
    xo.step.agent @= lambda x, *a, **kw: stepWrapper(x,role="agent",*a,**kw)


    print('='*10)
    cnt = 0
    processAIStep("System: <STAGE:0-init>\n", agent=sales_agent)
    while cnt !=max_num_turns:
        cnt+=1
        if cnt==max_num_turns:
            print('Maximum number of turns reached - ending the conversation.')
            break
        ai_message = sales_agent.step()

        processAIStep(ai_message, agent=sales_agent)

        # end conversation 
        if '<END_OF_CALL>' in sales_agent.conversation_history[-1]:
            print('Sales Agent determined it is time to end the conversation.')
            break

        
        
        human_input = ""
        c = 0
        while human_input =="":
            human_input = input('Your response: ')
            if c>1:
                print("<empty input ignored>")
            c+=1
        sales_agent.human_step(human_input)
        print('='*10)

     
'''
TODO: Run this
Changes: make async and connect with xoRedis
'''