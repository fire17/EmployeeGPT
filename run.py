import argparse

import os
import json
import time

from salesgpt.agents import SalesGPT
from langchain.chat_models import ChatOpenAI


from xo.redis import xoRedis

xo = xoRedis("test.engineergpt")

def processAIStep(msg, agent:SalesGPT):
    print(" ::: Processing Events")
    # print(msg)
    event_detected = "<STAGE" in msg.split("\n")[0]
    if event_detected:
        event = ":".join(msg.split("\n")[0].split(":")[1:])
        print("$"*10)
        stage_id = event.split(":")[1].split("-")[0].strip()
        stage_name = event.split("-")[1].split(">")[0].strip()
        print(f"Stage {stage_id} - {stage_name}")
        print("$"*10)
        
        def welcome_returning(manager_msg="[This is a returning customer, his last delivery address was 123 Ox st] (AUTOMATIC)",*a, **kw):
            print(" @@@ Adding Returning Client's Info @@@ !!!!!!!!! (AUTOMATIC)")
            print(manager_msg)
            # xo.step.manager = "[This is a returning customer, his last delivery address was 123 Ox st]"
            agent.manager_step(manager_msg)
        def send_bon(manager_msg = "[Sending payment link to customer] (AUTOMATIC)",
                     manager_msg2 = "[*Payment Successful*] (AUTOMATIC)", *a, **kw):
            
            print(" @@@ GENERATING & SENDING BON @@@")
            print(manager_msg)
            print(manager_msg2)
            # xo.step.manager = "[PAYMENT LINK SENT TO CLIENT !!!!!!!!! (AUTOMATIC) ] "
            agent.manager_step(manager_msg)
            agent.manager_step(manager_msg2)
        # print("::::::::::::: SUBS:",xo.step.manager._subscribers)
        def add_to_cart(*args, **kwargs):
            print(" @@@ UPDATING CART @@@ ")
        
        triggered_events = {"1":welcome_returning,"2":add_to_cart,"3":send_bon}
        if stage_id in triggered_events:
            triggered_events[stage_id]()
        else:
            print(f"----------STAGE{stage_id} not in {triggered_events}")
   

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
    parser.add_argument('--verbose', type=bool, help='Verbosity', default=True)
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
                                    product_catalog = "examples/sample_product_catalog.txt",
                                    salesperson_name="Ted Lasso",
                                    verbose=verbose)
        else:
            print("---BON EMPLOYEE---")
            sales_agent = SalesGPT.from_llm(llm, verbose=verbose)
    else:
        with open(config_path,'r') as f:
            config = json.load(f)
        print(f'Agent config {config}')
        sales_agent = SalesGPT.from_llm(llm, verbose=verbose, **config)


    sales_agent.seed_agent()

    def step(human_input, role="manager"):
        if role == "manager":
            sales_agent.manager_step(human_input)
        if role == "user":
            sales_agent.human_step(human_input)
        if role == "agent":
            sales_agent.step()

    
    def stepWrapper(i,*a, **kw):
        role="manager" if "role" not in kw else kw["role"]
        print("@@@@@@@@@@@@@@ STEPPING @@@@@@@@@@@@@@", i,":", a,":", kw)
        if i != None and i!=-1:
            return step(i, role=role)
        return None

    xo.step.manager = -1
    xo.step.user = -1
    xo.step.agent = -1
    # time.sleep(1)
    # def resetTriggers(xobj, triggers = ["manager","user","agent"]):
    #     for t in triggers:
    #         xobj[t] = -1
    # resetTriggers(xo.step)
    
    xo.step.manager._subscribers.clear()
    xo.step.user._subscribers.clear()
    xo.step.agent._subscribers.clear()
    xo.step.manager @= lambda x, *a, **kw: stepWrapper(x,role="manager",*a,**kw)
    xo.step.user @= lambda x, *a, **kw: stepWrapper(x,role="user",*a,**kw)
    xo.step.agent @= lambda x, *a, **kw: stepWrapper(x,role="agent",*a,**kw)


    print('='*10)
    cnt = 0
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

        

        human_input = input('Your response: ')
        sales_agent.human_step(human_input)
        print('='*10)

     
'''
TODO: Run this
Changes: make async and connect with xoRedis
'''