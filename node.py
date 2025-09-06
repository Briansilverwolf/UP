from base import SystemRequest,BusinessNeed, Sponsors, Capabilities , Values ,Issues
from langchain_core.messages import HumanMessage,SystemMessage
from model import chat_model, Zhipullm
import time

sleep_time = 3

#chat_model =Zhipullm

"""
System Request Nodes/ Functions
"""

def generate_business_need(state:SystemRequest):
    structured_chat = chat_model.with_structured_output(BusinessNeed)
    time.sleep(sleep_time)
    chat = structured_chat.invoke([
        SystemMessage(
        content="""
    You are an ultra-professional member of a steering committee, tasked with identifying business opportunities. 
    Your role is to take any input from the user—this could be a personal goal, an idea, or a vague ambition—and craft it into a 
    **well-defined, detailed business need**. 

    The business need should:
    - Clearly describe the **problem, opportunity, or driver** behind the user's idea.
    - Explain **why it is important** and what value it would create.
    - Avoid prescribing a specific solution (do not jump to implementation or goals yet).
    - Be detailed enough that it could guide strategy, planning, or a system request.

    Use professional, precise, and actionable language.
    """
    ),
    HumanMessage(
        content= state.input
    )

    ]
    
    )
    return {"business_need":chat.business_need}

def generate_sponsor(state:SystemRequest):
    structured = chat_model.with_structured_output(Sponsors)
    time.sleep(sleep_time)
    chat = structured.invoke(
        [
            SystemMessage(
                content=f"""
                based on the following information list out the appropriate sponsor of this business need.
                here is the original user input.
                {state.input}
                The user input was crafted to a valied business need that the project will be guided by
                {state.business_need}
                now. as a professional i want you to craft the list of the appropriate sponsor that will be needed for this project success
                """
            ),
            HumanMessage(
                content= "craft for me a list of must have sponsor to make sure that this project run smoothly"
            )
        ]
    )

    return {"project_sponsors":chat}

def generate_capabilities(state:SystemRequest):
    structured_chat = chat_model.with_structured_output(Capabilities)
    sponsors = "\n".join(f"{sponsor.name} : {sponsor.description}" for sponsor in state.project_sponsors.sponsors)
    time.sleep(sleep_time)
    chat = structured_chat.invoke(
        [
            SystemMessage(
                content =f"""
                Based on the following information you are to craft a list of features and capabilities gotten from the information below
                user input :
                {state.input}
                business need:
                {state.business_need}
                sponsors :
                {sponsors }
                now,  as a professional craft the features and the capabilities that this business is to have
                """
            ),
            HumanMessage(
                content = " list the features and the capabilies "
            )
        ]
    )
    return {"business_requirements":chat}

def generate_values(state:SystemRequest):
    structured_chat = chat_model.with_structured_output(Values)
    sponsors = "\n".join(f"{sponsor.name} : {sponsor.description}" for sponsor in state.project_sponsors.sponsors)
    capabilities = "\n".join(f"{feature.capability}" for feature in state.business_requirements.capabilities)
    time.sleep(sleep_time)
    chat = structured_chat.invoke(
        [
            SystemMessage(
                content = f"""
                Based on the following information you are to craft a list of business values gotten from the information below
                user input :
                {state.input}
                business need:
                {state.business_need}
                sponsors :
                {sponsors }
                capabilities :
                {capabilities}
                now,  as a professional craft business values that this business is to have
                """
            ),HumanMessage(
                content="provide the business values"
            )
        ]
    )

    return {"business_values": chat}

def generate_constraints(state: SystemRequest):
    structured_chat = chat_model.with_structured_output(Issues)
    sponsors = "\n".join(f"{sponsor.name} : {sponsor.description}" for sponsor in state.project_sponsors.sponsors)
    capabilities = "\n".join(f"{feature.capability}" for feature in state.business_requirements.capabilities)
    values = "\n".join(f"{value.value}" for value in state.business_values.values)
    time.sleep(sleep_time)
    chat = structured_chat.invoke(
        [
            SystemMessage(
                content=f"""
                Based on the following information you are to craft a list of business issues or the constraints gotten from the information below
                user input :
                {state.input}
                business need:
                {state.business_need}
                project sponsors :
                {sponsors }
                business capabilities and features:
                {capabilities}
                Business values  :
                {values}
                now,  as a professional craft business issues or the constraints that this business is to have
                """
            ),
            HumanMessage(
                content = "provide the business issues or the constraints"
            )
        ]
    )
    return {"constraits":chat}

    