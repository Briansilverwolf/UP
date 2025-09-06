from pydantic import BaseModel, Field

"""
System Request BaseModels
"""
class BusinessNeed(BaseModel):
    business_need :str = Field(..., description = "i varied unified process business need")
    BSN_id :int = Field(..., description="an id for the business need")

class Sponsor(BaseModel):
    id: int
    name: str =Field(...,description = "Name of the person who will serve as the primary contact for the project")
    description: str = Field(..., description= "Benefit or Roles of the sponsor to the business need")

class Sponsors(BaseModel):
    sponsors : list[Sponsor]

class Capability(BaseModel):
    id : int
    capability :str = Field(..., description = "The business features capabilty that the system will need to have")

class Capabilities(BaseModel):
    capabilities : list[Capability]

class Value(BaseModel):
    id :int
    value: str = Field(..., description="The benefits that the organization should expect from the system")

class Values(BaseModel):
    values : list[Value]

class Issue(BaseModel):
    id : int
    issue : str = Field(..., description="Catch-all for other information that should be considered in assessing the project.")

class Issues(BaseModel):
    issue : list[Issue]

class SystemRequest(BaseModel):
    input:str
    business_need: str = None
    project_sponsors: Sponsors = []
    business_requirements: Capabilities =[]
    business_values : Values= []
    constraits: Issues =[]

"""
Feasibility Study Models
"""