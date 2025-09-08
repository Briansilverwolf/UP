from typing import List, Optional, Union, Literal, Annotated, List, Dict, Set
from pydantic import BaseModel, Field,  model_validator

"""
System Request BaseModels
"""
class BusinessNeed(BaseModel):
    business_need: str = Field(..., description="i varied unified process business need")
    BSN_id: int = Field(..., description="an id for the business need")

class Sponsor(BaseModel):
    id: int
    name: str = Field(..., description="Name of the person who will serve as the primary contact for the project")
    description: str = Field(..., description="Benefit or Roles of the sponsor to the business need")

class Sponsors(BaseModel):
    sponsors: List[Sponsor] = Field(default_factory=list)

class Capability(BaseModel):
    id: int
    capability: str = Field(..., description="The business feature/capability that the system will need to have")

class Capabilities(BaseModel):
    capabilities: List[Capability] = Field(default_factory=list)

class Value(BaseModel):
    id: int
    value: str = Field(..., description="The benefits that the organization should expect from the system")

class Values(BaseModel):
    values: List[Value] = Field(default_factory=list)

class Issue(BaseModel):
    id: int
    issue: str = Field(..., description="Catch-all for other information that should be considered in assessing the project.")

class Issues(BaseModel):
    issues: List[Issue] = Field(default_factory=list)

class SystemRequest(BaseModel):
    input: str
    business_need: Optional[str] = None
    project_sponsors: Sponsors = Field(default_factory=Sponsors)
    business_requirements: Capabilities = Field(default_factory=Capabilities)
    business_values: Values = Field(default_factory=Values)
    constraints: Issues = Field(default_factory=Issues)


"""
Feasibility Analysis Models
"""
class FeasibilityFinding(BaseModel):
    id: int
    finding: str = Field(..., description="A specific finding or assessment point.")
    # fixed typo and normalized capitalization
    risk_level: Literal["Low", "Medium", "High"] = Field(..., description="Assessed risk.")

class FeasibilityAnalysis(BaseModel):
    system_request: SystemRequest  # Direct link to the request being analyzed
    technical_feasibility: List[FeasibilityFinding] = Field(default_factory=list, description="Can we build it?")
    economic_feasibility: List[FeasibilityFinding] = Field(default_factory=list, description="Should we build it?")
    organizational_feasibility: List[FeasibilityFinding] = Field(default_factory=list, description="If we build it, will they use it?")
    recommendation: str = Field(..., description="Overall recommendation (e.g., 'Proceed', 'Do Not Proceed').")


"""
Analysis Modeling

Requirement Defination
a document that lists 
the new systems capabilities. It then describes how to analyze requirements using requirements
analysis strategies and how to gather requirements using interviews, JAD sessions, 
quest
"""

class FunctionalRequirement(BaseModel):
    id: str
    description: str = Field(..., description="Process a system has to perform or information it needs to contain")
    priority: Literal["High", "Medium", "Low"] = Field(..., description="Priority.")

class NonFunctionalRequirement(BaseModel):
    id: str
    description: str = Field(..., description="Behavioral properties that the system must have, such as performance and usability.")
    type: Literal["Operational", "Performance", "Security", "Cultural", "Political"]

class RequirementDefinition(BaseModel):  # renamed from "RequirementDefination"
    requirements: List[Union[FunctionalRequirement, NonFunctionalRequirement]] = Field(default_factory=list)


"""
Use Case Diagram
"""

# --- Core Elements ---
class Actor(BaseModel):
    id: int = Field(..., description="Unique ID for the actor within its diagram.")
    name: str


class UseCase(BaseModel):
    id: int = Field(..., description="Unique ID for the use case within its diagram.")
    name: str

# --- Relationship Models ---
class Relationship(BaseModel):
    relationship_type: Literal["association", "include", "extend", "generalization"]
    source_id: int
    source_type: Literal["actor", "use_case"]
    target_id: int
    target_type: Literal["use_case", "actor"]

class UseCaseReference(BaseModel):
    diagram_id: int
    use_case_id: int

class CrossDiagramRelationship(BaseModel):
    relationship_type: Literal["include", "extend"]
    source: UseCaseReference
    target: UseCaseReference
  
# --- Validated Models ---
class UseCaseDiagram(BaseModel):
    id: int
    name: str
    actors: List[Actor] = Field(default_factory=list)
    use_cases: List[UseCase] = Field(default_factory=list, max_length=15)
    relationships: List[Relationship] = Field(default_factory=list)


class UseCaseModelCollection(BaseModel):
    project_name: str
    diagrams: List[UseCaseDiagram] = Field(default_factory=list)
    cross_diagram_relationships: List[CrossDiagramRelationship] = Field(default_factory=list)



"""
Activity Diagram
    Action
    Activity
    object Node
    control flow

"""


# --- Activity Elements ---
class ActivityNode(BaseModel):
    id: int
    name: str
    node_type: Literal["start", "end", "action", "decision", "merge", "fork", "join"]
    condition: Optional[str] = None  # For decision nodes

class ActivityFlow(BaseModel):
    source_id: int
    target_id: int
    condition: Optional[str] = None  # Guard condition

class Swimlane(BaseModel):
    id: int
    name: str
    actor_reference: Optional[int] = None  # Links to Actor from use case

# --- Use Case Link ---
class UseCaseLink(BaseModel):
    diagram_id: int
    use_case_id: int
    flow_step: str  # Which step this activity represents

class ActivityDiagram(BaseModel):
    id: int
    name: str
    use_case_links: List[UseCaseLink] = Field(default_factory=list)
    swimlanes: List[Swimlane] = Field(default_factory=list)
    nodes: List[ActivityNode] = Field(default_factory=list, max_length=25)
    flows: List[ActivityFlow] = Field(default_factory=list)


class ActivityModelCollection(BaseModel):
    project_name: str
    use_case_collection: 'UseCaseModelCollection'  # Forward ref
    activity_diagrams: List[ActivityDiagram] = Field(default_factory=list)

        


"""
Use case Description
"""

class Precondition(BaseModel):
    id: int
    condition: str

class Postcondition(BaseModel):
    id: int
    condition: str
    success: bool = True  # False for failure conditions

class Step(BaseModel):
    id: int
    actor: str
    action: str
    system_response: Optional[str] = None

class Extension(BaseModel):
    step_number: int  # Which step this extends
    condition: str
    steps: List[Step]
    return_to_step: Optional[int] = None  # Where to resume

class UseCaseDescription(BaseModel):
    use_case_id: int
    diagram_id: int
    
    # Core elements
    primary_actor: str
    goal: str
    scope: Literal["system", "business", "white-box", "black-box"] = "system"
    level: Literal["summary", "user-goal", "subfunction"] = "user-goal"
    
    # Conditions
    preconditions: List[Precondition] = Field(default_factory=list)
    success_guarantee: List[Postcondition] = Field(default_factory=list)
    minimal_guarantee: List[Postcondition] = Field(default_factory=list)
    
    # Flows
    main_success_scenario: List[Step] = Field(..., min_length=1)
    extensions: List[Extension] = Field(default_factory=list)
    
    # Meta
    frequency: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"

class UseCaseDescriptionCollection(BaseModel):
    project_name: str
    descriptions: List[UseCaseDescription] = Field(default_factory=list)
