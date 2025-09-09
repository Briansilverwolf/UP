from typing import List, Optional, Union, Literal, Annotated, List, Dict, Set, Any, Tuple
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
    project_name: str = Field(default = "change_later",description="appropriate name for this project")
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



"""
Structure Modeling
"""
"""
Object Identification
"""
class CandidateObject(BaseModel):
    """Represents a single potential object/class discovered during analysis."""
    id: int
    name: str = Field(..., description="The name of the candidate object (typically a noun).")
    
    discovery_method: Literal["textual_analysis", "brainstorming", "common_object_list", "pattern"] = Field(
        ..., description="The technique that first identified this candidate."
    )
    
    category: Optional[Literal["physical", "role", "event", "interaction", "abstract"]] = Field(
        None, description="Classification based on common object lists."
    )
    
    status: Literal["candidate", "accepted", "rejected", "merged"] = Field(
        default="candidate", description="The current state of this candidate in the analysis process."
    )
    
    justification: Optional[str] = Field(
        None, description="Reasoning for the current status (e.g., 'Rejected: Out of scope', 'Merged into User class')."
    )
    
    merged_into_id: Optional[int] = Field(
        None, description="If status is 'merged', this points to the ID of the object it was merged into."
    )

class ObjectIdentificationSession(BaseModel):
    """
    Represents the entire object identification process for a given problem domain.
    It holds the source text and the single, evolving list of candidate objects.
    """
    domain_description: str = Field(
        ..., description="The source text (e.g., use case) used for textual analysis."
    )
    
    candidate_objects: List[CandidateObject] = Field(
        default_factory=list, 
        description="A single, unified list of all candidate objects discovered and analyzed."
    )

    def get_finalized_classes(self) -> List[CandidateObject]:
        """A helper method to easily retrieve the final list of accepted classes."""
        return [obj for obj in self.candidate_objects if obj.status == "accepted"]

    """
    Why This Model is Better
        Single Source of Truth: There is only one list, candidate_objects. An object's entire history is contained within its own properties.
        Reflects the Process: The status field (candidate -> accepted/rejected/merged) perfectly models the filtering lifecycle.
        Enhanced Traceability: The justification field provides critical project memory, explaining why decisions were made. The merged_into_id field explicitly tracks refinement.
        Completeness: It includes brainstorming as a discovery method and uses the book's terminology.
        Practicality: The get_finalized_classes() helper method makes it easy to get the final result without cluttering the core data model.

    """

"""
Class-Responsibility-colaborator
"""

class Responsibility(BaseModel):
    """Represents a single responsibility and the collaborators needed to fulfill it."""
    description: str = Field(..., description="A short verb phrase describing what the class does or knows.")
    
    collaborators: List[str] = Field(
        default_factory=list, 
        description="List of other class names this class must interact with for this specific responsibility."
    )

class CRCCard(BaseModel):
    """Models a single Class-Responsibility-Collaboration card."""
    class_name: str = Field(..., description="The name of the class (singular noun).")
    description: str = Field(..., description="A brief sentence describing the purpose of the class.")
    
    # Inheritance relationships
    superclass: Optional[str] = Field(None, description="The name of the parent class, if any.")
    subclasses: List[str] = Field(default_factory=list, description="List of child classes, if any.")
    
    # Responsibilities are split into "knowing" (attributes) and "doing" (methods)
    attributes: List[str] = Field(
        default_factory=list, 
        description="The 'knowing' responsibilities, which will become attributes."
    )
    
    responsibilities: List[Responsibility] = Field(
        default_factory=list,
        description="The 'doing' responsibilities, which will become methods."
    )

class CRCModel(BaseModel):
    """
    Represents the entire collection of CRC cards for a system or subsystem.
    This class is responsible for ensuring the integrity of the entire model.
    """
    project_name: str
    cards: List[CRCCard]
    
    @model_validator(mode='after')
    def validate_collaborations_and_inheritance(self):
        """
        Ensures that every collaborator and super/subclass mentioned on a card
        corresponds to another valid card in the model. This is critical for
        maintaining the integrity of the object model.
        """
        # Create a set of all valid class names for fast lookups
        valid_class_names: Set[str] = {card.class_name for card in self.cards}
        
        for card in self.cards:
            # Validate superclass
            if card.superclass and card.superclass not in valid_class_names:
                raise ValueError(f"On card '{card.class_name}', superclass '{card.superclass}' does not exist in the model.")
            
            # Validate subclasses
            for subclass in card.subclasses:
                if subclass not in valid_class_names:
                    raise ValueError(f"On card '{card.class_name}', subclass '{subclass}' does not exist in the model.")
            
            # Validate collaborators within each responsibility
            for resp in card.responsibilities:
                for collaborator in resp.collaborators:
                    if collaborator not in valid_class_names:
                        raise ValueError(
                            f"Validation Error on card '{card.class_name}': "
                            f"Responsibility '{resp.description}' has an invalid collaborator '{collaborator}'. "
                            f"'{collaborator}' is not a defined class in this model."
                        )
        return self

"""
Class Diagram
"""   
Visibility = Literal["public", "private", "protected"]

class Attribute(BaseModel):
    """Models an attribute of a class."""
    name: str
    type: str = Field("string", description="The data type of the attribute (e.g., string, int, bool, or another class name).")
    visibility: Visibility = "private"

class Parameter(BaseModel):
    """Models a single parameter for a method."""
    name: str
    type: str

class Method(BaseModel):
    """Models a method (operation) of a class."""
    name: str
    parameters: List[Parameter] = Field(default_factory=list)
    return_type: str = Field("void", description="The data type returned by the method.")
    visibility: Visibility = "public"

class UMLClass(BaseModel):
    """Models a single class in the diagram."""
    name: str = Field(..., description="The unique name of the class.")
    description: str = Field(..., description="A brief description of the class's purpose.")
    is_abstract: bool = False
    attributes: List[Attribute] = Field(default_factory=list)
    methods: List[Method] = Field(default_factory=list)

class Generalization(BaseModel):
    """Models an inheritance relationship (is-a)."""
    subclass: str = Field(..., description="The name of the class that inherits.")
    superclass: str = Field(..., description="The name of the class being inherited from.")

class Association(BaseModel):
    """Models an association, aggregation, or composition relationship."""
    type: Literal["association", "aggregation", "composition"] = "association"
    
    # Defines the two ends of the relationship
    class1_name: str
    class1_multiplicity: str = Field("1", description="e.g., '1', '0..1', '0..*', '*'")
    
    class2_name: str
    class2_multiplicity: str = Field("1", description="e.g., '1', '0..1', '0..*', '*'")
    
    description: Optional[str] = Field(None, description="An optional description of the relationship's meaning.")

class ClassDiagram(BaseModel):
    """
    Represents a complete Class Diagram, containing all classes and their relationships.
    This model enforces the structural integrity of the diagram.
    """
    project_name: str
    classes: List[UMLClass]
    associations: List[Association] = Field(default_factory=list)
    generalizations: List[Generalization] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_diagram_integrity(self):
        """
        Ensures the entire diagram is logically consistent:
        1. Class names are unique.
        2. All relationships refer to existing classes.
        3. Generalization (inheritance) is not circular.
        """
        # 1. Check for unique class names
        class_names: Set[str] = {cls.name for cls in self.classes}
        if len(class_names) != len(self.classes):
            raise ValueError("Duplicate class names found in the diagram.")
            
        # 2. Validate all relationships
        for assoc in self.associations:
            if assoc.class1_name not in class_names:
                raise ValueError(f"Association error: Class '{assoc.class1_name}' not found in the diagram.")
            if assoc.class2_name not in class_names:
                raise ValueError(f"Association error: Class '{assoc.class2_name}' not found in the diagram.")
        
        for gen in self.generalizations:
            if gen.subclass not in class_names:
                raise ValueError(f"Generalization error: Subclass '{gen.subclass}' not found in the diagram.")
            if gen.superclass not in class_names:
                raise ValueError(f"Generalization error: Superclass '{gen.superclass}' not found in the diagram.")
        
        # 3. Check for circular inheritance (e.g., A inherits B, B inherits A)
        # We build a dependency graph and check for cycles.
        inheritance_graph: Dict[str, str] = {gen.subclass: gen.superclass for gen in self.generalizations}
        for start_node in inheritance_graph:
            path = {start_node}
            curr_node = start_node
            while curr_node in inheritance_graph:
                curr_node = inheritance_graph[curr_node]
                if curr_node in path:
                    raise ValueError(f"Circular inheritance detected involving class '{curr_node}'.")
                path.add(curr_node)
        
        return self



"""
Object Diagram
"""
class UMLClass(BaseModel): name: str; attributes: List[Attribute] = []; # Simplified for context
class Attribute(BaseModel): name: str
class Association(BaseModel): class1_name: str; class2_name: str
class ClassDiagram(BaseModel): classes: List[UMLClass]; associations: List[Association] = []


class AttributeValue(BaseModel):
    """Represents a specific value for an attribute of an object."""
    name: str = Field(..., description="The name of the attribute, must match the class definition.")
    value: Any = Field(..., description="The concrete value of the attribute at a moment in time.")

class DiagramObject(BaseModel):
    """Models a single object (an instance of a class)."""
    instance_name: str = Field(..., description="The unique name for this instance in the diagram (e.g., 'prof_hawking').")
    class_name: str = Field(..., description="The name of the class this object is an instance of (e.g., 'Professor').")
    attribute_values: List[AttributeValue] = Field(
        default_factory=list,
        description="The state of the object, showing specific values for its attributes."
    )

class Link(BaseModel):
    """Models a link (an instance of an association) between two objects."""
    object1_instance_name: str = Field(..., description="The instance name of the first object in the link.")
    object2_instance_name: str = Field(..., description="The instance name of the second object in the link.")
    association_description: Optional[str] = Field(None, description="Optional text describing the link's purpose.")

class ObjectDiagram(BaseModel):
    """
    Represents a complete Object Diagram. It is a snapshot of object instances
    that MUST be consistent with a corresponding Class Diagram.
    """
    name: str = Field(..., description="A name for this specific scenario or snapshot (e.g., 'Successful Course Registration').")
    
    # The source of truth for validation
    class_diagram: ClassDiagram
    
    # The instances and links in this snapshot
    objects: List[DiagramObject]
    links: List[Link] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_against_class_diagram(self):
        """
        This is the most critical validator. It ensures that this Object Diagram
        is a legal and valid instantiation of the provided Class Diagram.
        """
        class_diagram = self.class_diagram
        
        # --- Step 1: Build efficient lookups from the Class Diagram ---
        class_map: Dict[str, UMLClass] = {cls.name: cls for cls in class_diagram.classes}
        
        # Create a set of valid associations. Store as a sorted tuple to make the relationship non-directional.
        valid_associations: Set[Tuple[str, str]] = {
            tuple(sorted((asc.class1_name, asc.class2_name))) for asc in class_diagram.associations
        }

        # --- Step 2: Validate the objects ---
        object_map: Dict[str, DiagramObject] = {}
        for obj in self.objects:
            # Check for unique instance names
            if obj.instance_name in object_map:
                raise ValueError(f"Duplicate instance name '{obj.instance_name}' found in the object diagram.")
            object_map[obj.instance_name] = obj

            # Check if the object's class exists in the Class Diagram
            if obj.class_name not in class_map:
                raise ValueError(f"Object '{obj.instance_name}' is an instance of '{obj.class_name}', which is not a defined class in the Class Diagram.")
            
            # Check if the object's attributes are valid for its class
            uml_class = class_map[obj.class_name]
            valid_attribute_names: Set[str] = {attr.name for attr in uml_class.attributes}
            for attr_val in obj.attribute_values:
                if attr_val.name not in valid_attribute_names:
                    raise ValueError(
                        f"Object '{obj.instance_name}' of class '{obj.class_name}' has an invalid attribute '{attr_val.name}'. "
                        f"Valid attributes are: {list(valid_attribute_names)}."
                    )

        # --- Step 3: Validate the links ---
        for link in self.links:
            # Check if linked objects exist in this diagram
            if link.object1_instance_name not in object_map:
                raise ValueError(f"Link error: Object '{link.object1_instance_name}' not found in the diagram.")
            if link.object2_instance_name not in object_map:
                raise ValueError(f"Link error: Object '{link.object2_instance_name}' not found in the diagram.")

            # Check if a corresponding association exists in the Class Diagram
            obj1 = object_map[link.object1_instance_name]
            obj2 = object_map[link.object2_instance_name]
            association_key = tuple(sorted((obj1.class_name, obj2.class_name)))
            
            if association_key not in valid_associations:
                raise ValueError(
                    f"Invalid link between '{obj1.instance_name}:{obj1.class_name}' and '{obj2.instance_name}:{obj2.class_name}'. "
                    f"No corresponding association exists between '{obj1.class_name}' and '{obj2.class_name}' in the Class Diagram."
                )
        
        return self


"""
UML Model
"""

class UMLModel(BaseModel):
    input: str
    request: SystemRequest = Field(default_factory=SystemRequest)
    feasibility: Optional[FeasibilityAnalysis] = None  # absent until generated
    requirement: RequirementDefinition = Field(default_factory=RequirementDefinition)
    usecase: UseCaseModelCollection = Field(default_factory=UseCaseModelCollection)
    activity: ActivityModelCollection = Field(default_factory=ActivityModelCollection)
    use_case_descriptions: UseCaseDescriptionCollection = Field(default_factory=UseCaseDescriptionCollection)
    

