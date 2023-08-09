from copy import deepcopy
from typing import Any, Dict, List, Union

from langchain import LLMChain
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.chains import RetrievalQA
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from pydantic import BaseModel, Field

from salesgpt.chains import SalesConversationChain, StageAnalyzerChain
from salesgpt.logger import time_logger
from salesgpt.parsers import SalesConvoOutputParser
from salesgpt.prompts import SALES_AGENT_TOOLS_PROMPT
from salesgpt.stages import CONVERSATION_STAGES
from salesgpt.templates import CustomPromptTemplateForTools
from salesgpt.tools import get_tools, setup_knowledge_base

Tool_master = False



class SalesGPT(Chain, BaseModel):
    """Controller model for the Sales Agent."""

    conversation_history: List[str] = []
    conversation_stage_id: str = "1"
    current_conversation_stage: str = CONVERSATION_STAGES.get("1")
    stage_analyzer_chain: StageAnalyzerChain = Field(...)
    sales_agent_executor: Union[AgentExecutor, None] = Field(...)
    knowledge_base: Union[RetrievalQA, None] = Field(...)
    sales_conversation_utterance_chain: SalesConversationChain = Field(...)
    conversation_stage_dict: Dict = CONVERSATION_STAGES

    use_tools: bool = False
    salesperson_name: str = "Ace"
    # salesperson_role: str = "Business Development Representative"
    salesperson_role: str = "Business Employee"
    company_name: str = "Ace's Beers"
    company_business: str = "We have a family owned shop in Arsuf, and we make the best beers around."
    # company_values: str = "Our mission at Sleep Haven is to help people achieve a better night's sleep by providing them with the best possible sleep solutions. We believe that quality sleep is essential to overall health and well-being, and we are committed to helping our customers achieve optimal sleep by offering exceptional products and customer service."
    company_values: str = "We are here 24/7 to deliver you beer right to your doorstep. We sell our beers as well as other providers at low cost."
    conversation_purpose: str = "Ask them what they would like to order, and answer any questions they have."
    conversation_type: str = "call"

    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, "1")

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    @time_logger
    def seed_agent(self):
        # Step 1: seed the conversation
        self.current_conversation_stage = self.retrieve_conversation_stage("1")
        self.conversation_history = []

    @time_logger
    def determine_conversation_stage(self):
        self.conversation_stage_id = self.stage_analyzer_chain.run(
            conversation_history="\n".join(self.conversation_history).rstrip("\n"),
            conversation_stage_id=self.conversation_stage_id,
            conversation_stages="\n".join(
                [
                    str(key) + ": " + str(value)
                    for key, value in CONVERSATION_STAGES.items()
                ]
            ),
        )

        print(f"Conversation Stage ID: {self.conversation_stage_id}")
        self.current_conversation_stage = self.retrieve_conversation_stage(
            self.conversation_stage_id
        )

        print(f"Conversation Stage: {self.current_conversation_stage}")

    def human_step(self, human_input):
        # process human input
        human_input = "Customer: " + human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    def manager_step(self, human_input):
        # process human input
        human_input = "Manager: " + human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    def System_step(self, system_input):
        # process system input
        system_input = "System: " + system_input + " <END_OF_TURN>"
        self.conversation_history.append(system_input)

    @time_logger
    def step(
        self, return_streaming_generator: bool = False, model_name="gpt-3.5-turbo-0613"
    ):
        """
        Args:
            return_streaming_generator (bool): whether or not return
            streaming generator object to manipulate streaming chunks in downstream applications.
        """
        if not return_streaming_generator:
            return self._call(inputs={})
        else:
            return self._streaming_generator(model_name=model_name)

    # TO-DO change this override "run" override the "run method" in the SalesConversation chain!
    @time_logger
    def _streaming_generator(self, model_name="gpt-3.5-turbo-0613"):
        """
        Sometimes, the sales agent wants to take an action before the full LLM output is available.
        For instance, if we want to do text to speech on the partial LLM output.

        This function returns a streaming generator which can manipulate partial output from an LLM
        in-flight of the generation.

        Example:

        >> streaming_generator = self._streaming_generator()
        # Now I can loop through the output in chunks:
        >> for chunk in streaming_generator:
        Out: Chunk 1, Chunk 2, ... etc.
        See: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
        """
        prompt = self.sales_conversation_utterance_chain.prep_prompts(
            [
                dict(
                    conversation_stage=self.current_conversation_stage,
                    conversation_history="\n".join(self.conversation_history),
                    salesperson_name=self.salesperson_name,
                    salesperson_role=self.salesperson_role,
                    company_name=self.company_name,
                    company_business=self.company_business,
                    company_values=self.company_values,
                    conversation_purpose=self.conversation_purpose,
                    conversation_type=self.conversation_type,
                )
            ]
        )

        inception_messages = prompt[0][0].to_messages()

        message_dict = {"role": "system", "content": inception_messages[0].content}

        if self.sales_conversation_utterance_chain.verbose:
            print("\033[92m" + inception_messages[0].content + "\033[0m")
        messages = [message_dict]

        return self.sales_conversation_utterance_chain.llm.completion_with_retry(
            messages=messages,
            stop="<END_OF_TURN>",
            stream=True,
            model=model_name,
        )

    def _call(self, inputs: Dict[str, Any]) -> None:
        """Run one step of the sales agent."""

        # Generate agent's utterance
        # if use tools
        if Tool_master and self.use_tools:
            ai_message = self.sales_agent_executor.run(
                input="",
                conversation_stage=self.current_conversation_stage,
                conversation_history="\n".join(self.conversation_history),
                salesperson_name=self.salesperson_name,
                salesperson_role=self.salesperson_role,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                conversation_purpose=self.conversation_purpose,
                conversation_type=self.conversation_type,
            )

        else:
            # else
            ai_message = self.sales_conversation_utterance_chain.run(
                conversation_stage=self.current_conversation_stage,
                conversation_history="\n".join(self.conversation_history),
                salesperson_name=self.salesperson_name,
                salesperson_role=self.salesperson_role,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                conversation_purpose=self.conversation_purpose,
                conversation_type=self.conversation_type,
            )

        # Add agent's response to conversation history
        raw_output = ai_message
        agent_name = self.salesperson_name
        ai_message = agent_name + ": " + ai_message
        if '<END_OF_TURN>' not in ai_message:
            ai_message += ' <END_OF_TURN>'
        #TODO: check for <EVENTS> in ai_message + add them to ai_message / conversation_history
        self.conversation_history.append(ai_message)
        SalesGPT.pretty(ai_message.replace("<END_OF_TURN>", ""))
        #TODO: Send results back to client, after event filter, 
        return ai_message
    
    @classmethod
    def pretty(cls, ai_message):
        for line in ai_message.split('\n'):
            if "<" in ":".join(line.split(":")[1:]).strip()[:1]:
                if "<STAGE" in line:
                    print("\033[93m" + line + "\033[0m")
                else:
                    print("\033[92m" + line + "\033[0m")
            else:
                print(line)


    @classmethod
    @time_logger
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "SalesGPT":
        """Initialize the SalesGPT Controller."""
        stage_analyzer_chain = StageAnalyzerChain.from_llm(llm, verbose=verbose)
        if (
            "use_custom_prompt" in kwargs.keys()
            and kwargs["use_custom_prompt"] == "True"
            and False
        ):
            use_custom_prompt = deepcopy(kwargs["use_custom_prompt"])
            custom_prompt = deepcopy(kwargs["custom_prompt"])

            # clean up
            del kwargs["use_custom_prompt"]
            del kwargs["custom_prompt"]

            sales_conversation_utterance_chain = SalesConversationChain.from_llm(
                llm,
                verbose=verbose,
                use_custom_prompt=use_custom_prompt,
                custom_prompt=custom_prompt,
            )

        else:
            sales_conversation_utterance_chain = SalesConversationChain.from_llm(
                llm, verbose=verbose
            )

        if Tool_master and ("use_tools" in kwargs.keys() and kwargs["use_tools"] is True):
            # set up agent with tools
            menu = kwargs["menu"] if "menu" in kwargs else ""
            salesperson_name = kwargs["salesperson_name"] if "salesperson_name" in kwargs else "Dani" 
            # class customKBase(BaseModel):
            #     def run(*args, **kwargs) -> Dict:
            #         print("################# ############ #### # # # #  # # CUSTOM KNOLEGE BASE",args,kwargs)
            #         return {**kwargs,**{"retriever":Dict.__new__({})}}
            knowledge_base = setup_knowledge_base(menu)
            # knowledge_base = setup_knowledge_base("product_catalog")
            # knowledge_base: Dict = customKBase.run()
            tools = get_tools(knowledge_base)

            prompt = CustomPromptTemplateForTools(
                template=SALES_AGENT_TOOLS_PROMPT,
                tools_getter=lambda x: tools,
                # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
                # This includes the `intermediate_steps` variable because that is needed
                input_variables=[
                    "input",
                    "intermediate_steps",
                    "salesperson_name",
                    "salesperson_role",
                    "company_name",
                    "company_business",
                    "company_values",
                    "conversation_purpose",
                    "conversation_type",
                    "conversation_history",
                ],
            )
            llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

            tool_names = [tool.name for tool in tools]

            # WARNING: this output parser is NOT reliable yet
            ## It makes assumptions about output from LLM which can break and throw an error
            output_parser = SalesConvoOutputParser(ai_prefix=salesperson_name)

            sales_agent_with_tools = LLMSingleActionAgent(
                llm_chain=llm_chain,
                output_parser=output_parser,
                # stop=["\nObservation:"],
                stop=["\nThought: Do"],
                allowed_tools=tool_names,
            )

            sales_agent_executor = AgentExecutor.from_agent_and_tools(
                agent=sales_agent_with_tools, tools=tools, verbose=verbose
            )
        else:
            sales_agent_executor = None
            knowledge_base = None

        return cls(
            stage_analyzer_chain=stage_analyzer_chain,
            sales_conversation_utterance_chain=sales_conversation_utterance_chain,
            sales_agent_executor=sales_agent_executor, # Default when using tools
            knowledge_base=knowledge_base,
            verbose=verbose,
            **kwargs,
        )

'''
TODO: This is where the meat setup is
Changes: changed salesman to Ace beer (bon) employee
'''