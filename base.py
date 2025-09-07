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
    description: str

class UseCaseDescription(BaseModel):
    normal_flow: List[str] = Field(..., description="The step-by-step 'happy path'.")
    alternative_flows: List[str] = Field(default_factory=list, description="Alternate paths or exceptions.")

         
class UseCase(BaseModel):
    id: int = Field(..., description="Unique ID for the use case within its diagram.")
    name: str
    description: str # Role a user have to the system
    details: UseCaseDescription

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
    description: str

# --- Validated Models ---
class UseCaseDiagram(BaseModel):
    id: int
    name: str
    actors: List[Actor] = Field(default_factory=list)
    use_cases: List[UseCase] = Field(default_factory=list, max_length=15)
    relationships: List[Relationship] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_constraints(self):
        # Check unique IDs
        actor_ids = [a.id for a in self.actors]
        use_case_ids = [uc.id for uc in self.use_cases]
        
        if len(set(actor_ids)) != len(actor_ids):
            raise ValueError(f"Diagram {self.id}: Duplicate actor IDs")
        if len(set(use_case_ids)) != len(use_case_ids):
            raise ValueError(f"Diagram {self.id}: Duplicate use case IDs")
        
        # Validate relationships
        actor_id_set: Set[int] = set(actor_ids)
        use_case_id_set: Set[int] = set(use_case_ids)

        for rel in self.relationships:
            if rel.source_type == 'actor' and rel.source_id not in actor_id_set:
                raise ValueError(f"Diagram {self.id}: Invalid source actor {rel.source_id}")
            if rel.source_type == 'use_case' and rel.source_id not in use_case_id_set:
                raise ValueError(f"Diagram {self.id}: Invalid source use case {rel.source_id}")
            if rel.target_type == 'actor' and rel.target_id not in actor_id_set:
                raise ValueError(f"Diagram {self.id}: Invalid target actor {rel.target_id}")
            if rel.target_type == 'use_case' and rel.target_id not in use_case_id_set:
                raise ValueError(f"Diagram {self.id}: Invalid target use case {rel.target_id}")
        
        return self

class UseCaseModelCollection(BaseModel):
    project_name: str
    diagrams: List[UseCaseDiagram] = Field(default_factory=list)
    cross_diagram_relationships: List[CrossDiagramRelationship] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_cross_references(self):
        # Build reference map
        valid_refs: Dict[int, Set[int]] = {
            d.id: {uc.id for uc in d.use_cases} for d in self.diagrams
        }
        
        # Check unique diagram IDs
        diagram_ids = [d.id for d in self.diagrams]
        if len(set(diagram_ids)) != len(diagram_ids):
            raise ValueError("Duplicate diagram IDs")

        # Validate cross-relationships
        for i, cross_rel in enumerate(self.cross_diagram_relationships):
            src, tgt = cross_rel.source, cross_rel.target
            
            if src.diagram_id not in valid_refs:
                raise ValueError(f"Cross-rel {i}: Invalid source diagram {src.diagram_id}")
            if src.use_case_id not in valid_refs[src.diagram_id]:
                raise ValueError(f"Cross-rel {i}: Invalid source use case {src.use_case_id}")
            
            if tgt.diagram_id not in valid_refs:
                raise ValueError(f"Cross-rel {i}: Invalid target diagram {tgt.diagram_id}")
            if tgt.use_case_id not in valid_refs[tgt.diagram_id]:
                raise ValueError(f"Cross-rel {i}: Invalid target use case {tgt.use_case_id}")
        
        return self

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

    @model_validator(mode='after')
    def validate_structure(self):
        node_ids = {n.id for n in self.nodes}
        
        # Unique node IDs
        if len(node_ids) != len(self.nodes):
            raise ValueError(f"Activity {self.id}: Duplicate node IDs")
        
        # Start/end nodes
        start_nodes = [n for n in self.nodes if n.node_type == "start"]
        end_nodes = [n for n in self.nodes if n.node_type == "end"]
        
        if len(start_nodes) != 1:
            raise ValueError(f"Activity {self.id}: Must have exactly 1 start node")
        if len(end_nodes) < 1:
            raise ValueError(f"Activity {self.id}: Must have at least 1 end node")
        
        # Valid flows
        for flow in self.flows:
            if flow.source_id not in node_ids:
                raise ValueError(f"Activity {self.id}: Invalid source {flow.source_id}")
            if flow.target_id not in node_ids:
                raise ValueError(f"Activity {self.id}: Invalid target {flow.target_id}")
        
        return self

class ActivityModelCollection(BaseModel):
    project_name: str
    use_case_collection: 'UseCaseModelCollection'  # Forward ref
    activity_diagrams: List[ActivityDiagram] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_use_case_links(self):
        # Build valid use case map
        valid_use_cases: Dict[int, Set[int]] = {
            d.id: {uc.id for uc in d.use_cases} 
            for d in self.use_case_collection.diagrams
        }
        
        for diagram in self.activity_diagrams:
            for link in diagram.use_case_links:
                if link.diagram_id not in valid_use_cases:
                    raise ValueError(f"Activity {diagram.id}: Invalid use case diagram {link.diagram_id}")
                if link.use_case_id not in valid_use_cases[link.diagram_id]:
                    raise ValueError(f"Activity {diagram.id}: Invalid use case {link.use_case_id}")
        
        return 
        


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

    @model_validator(mode='after')
    def validate_steps(self):
        # Unique step IDs in main flow
        step_ids = {s.id for s in self.main_success_scenario}
        if len(step_ids) != len(self.main_success_scenario):
            raise ValueError(f"UC {self.use_case_id}: Duplicate main step IDs")
        
        # Extension validation
        max_step = max(s.id for s in self.main_success_scenario)
        for ext in self.extensions:
            if ext.step_number > max_step:
                raise ValueError(f"UC {self.use_case_id}: Extension references invalid step {ext.step_number}")
            if ext.return_to_step and ext.return_to_step > max_step:
                raise ValueError(f"UC {self.use_case_id}: Invalid return step {ext.return_to_step}")
        
        return self

class UseCaseDescriptionCollection(BaseModel):
    project_name: str
    descriptions: List[UseCaseDescription] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_uniqueness(self):
        keys = {(d.diagram_id, d.use_case_id) for d in self.descriptions}
        if len(keys) != len(self.descriptions):
            raise ValueError("Duplicate use case descriptions")
        return self