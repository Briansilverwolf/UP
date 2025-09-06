from langgraph.graph import StateGraph, START, END
from node import SystemRequest as SystemRequestState,generate_business_need, generate_sponsor, generate_capabilities, generate_values, generate_constraints
from serializer import model_to_json

"""
System request Graph, accept the user idea, goal and output a system request
""" 

SystemRequest = StateGraph(SystemRequestState)


#Genearting the Graph Nodes
SystemRequest.add_node("business_need",generate_business_need)
SystemRequest.add_node("sponsors",generate_sponsor)
SystemRequest.add_node("capabilities",generate_capabilities)
SystemRequest.add_node("values",generate_values)
SystemRequest.add_node("constraints",generate_constraints)


#  Connecting the Node To create te Workflow
SystemRequest.add_edge(START,"business_need")
SystemRequest.add_edge("business_need","sponsors")
SystemRequest.add_edge("sponsors","capabilities")
SystemRequest.add_edge("capabilities","values")
SystemRequest.add_edge("values","constraints")
SystemRequest.add_edge("constraints",END)

def systemRequest() -> StateGraph:
    return SystemRequest

""""

"""


"""

for x,y in output.items():
    #print(f"{x} : {y}")
    if x == "business_need":
        print(f"{x} : {y}")
    if x == "project_sponsors":
        print(y.sponsors)
        for sponsor in y["Sponsor"]:
            print(sponsor)
            print(f"{sponsor.name} -> {sponsor.description}")
    if x == "business_requirements":
        for capability in y:
            print(f"{capability.id}: {capability.capability}")
    if x == "business_values":
        for value in y:
            print(f"{value.id}: {value.value}")
    if x == "constraits":
        for issue in y:
            print(f"{issue.id}: {issue.issue}")
    print()

"""


