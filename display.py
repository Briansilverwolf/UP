from base import UseCaseDescriptionCollection, UseCaseDescription, ActivityDiagram,ActivityModelCollection, UseCaseDiagram,UseCaseModelCollection
def generate_plantuml_usecase(collection: UseCaseDescriptionCollection) -> str:
    """Convert UseCaseDescriptionCollection to PlantUML use case diagram"""
    
    lines = ["@startuml", f"title {collection.project_name} - Use Cases", ""]
    
    # Extract unique actors
    actors = set()
    for desc in collection.descriptions:
        actors.add(desc.primary_actor)
        for step in desc.main_success_scenario:
            actors.add(step.actor)
        for ext in desc.extensions:
            for step in ext.steps:
                actors.add(step.actor)
    
    # Define actors
    for actor in sorted(actors):
        lines.append(f"actor {actor}")
    lines.append("")
    
    # Define use cases and relationships
    for desc in collection.descriptions:
        uc_name = f"UC{desc.use_case_id}"
        lines.append(f"usecase {uc_name} as \"{desc.goal}\"")
        lines.append(f"{desc.primary_actor} --> {uc_name}")
        lines.append("")
    
    lines.append("@enduml")
    return "\n".join(lines)


def generate_detailed_plantuml(desc: UseCaseDescription) -> str:
    """Generate detailed PlantUML for single use case with notes"""
    
    lines = ["@startuml", f"title UC{desc.use_case_id}: {desc.goal}", ""]
    
    # Actors
    actors = {desc.primary_actor}
    for step in desc.main_success_scenario:
        actors.add(step.actor)
    
    for actor in sorted(actors):
        lines.append(f"actor {actor}")
    lines.append("")
    
    # Use case
    uc_name = f"UC{desc.use_case_id}"
    lines.append(f"usecase {uc_name} as \"{desc.goal}\"")
    lines.append(f"{desc.primary_actor} --> {uc_name}")
    lines.append("")
    
    # Notes with details
    notes = []
    
    # Preconditions
    if desc.preconditions:
        notes.append("**Preconditions:**")
        for pre in desc.preconditions:
            notes.append(f"• {pre.condition}")
        notes.append("")
    
    # Main flow
    notes.append("**Main Success Scenario:**")
    for step in desc.main_success_scenario:
        resp = f" -> {step.system_response}" if step.system_response else ""
        notes.append(f"{step.id}. {step.actor}: {step.action}{resp}")
    notes.append("")
    
    # Extensions
    if desc.extensions:
        notes.append("**Extensions:**")
        for ext in desc.extensions:
            notes.append(f"{ext.step_number}a. If {ext.condition}:")
            for step in ext.steps:
                resp = f" -> {step.system_response}" if step.system_response else ""
                notes.append(f"  {step.id}. {step.actor}: {step.action}{resp}")
            if ext.return_to_step:
                notes.append(f"  Resume at step {ext.return_to_step}")
        notes.append("")
    
    # Success guarantee
    if desc.success_guarantee:
        notes.append("**Success Guarantee:**")
        for post in desc.success_guarantee:
            notes.append(f"• {post.condition}")
    
    # Add note to diagram
    note_text = "\n".join(notes)
    lines.append(f"note right of {uc_name}")
    lines.append(note_text)
    lines.append("end note")
    lines.append("")
    
    lines.append("@enduml")
    return "\n".join(lines)


# Usage examples:
# plantuml_overview = generate_plantuml_usecase(your_collection)
# plantuml_detailed = generate_detailed_plantuml(your_collection.descriptions[0])

def generate_plantuml_activity(diagram: ActivityDiagram) -> str:
    """Convert ActivityDiagram to PlantUML activity diagram"""
    
    lines = ["@startuml", f"title {diagram.name}", ""]
    
    # Add use case links as notes if present
    if diagram.use_case_links:
        lines.append("note top")
        lines.append("**Linked Use Cases:**")
        for link in diagram.use_case_links:
            lines.append(f"• UC{link.use_case_id} (Diagram {link.diagram_id}): {link.flow_step}")
        lines.append("end note")
        lines.append("")
    
    # Generate swimlanes if present
    swimlane_map = {sl.id: sl.name for sl in diagram.swimlanes}
    if diagram.swimlanes:
        for swimlane in diagram.swimlanes:
            lines.append(f"|{swimlane.name}|")
            
            # Find nodes in this swimlane (assuming node names contain swimlane reference)
            # Since there's no direct swimlane assignment, we'll group all nodes for now
            break  # Only add swimlane structure once
        lines.append("")
    
    # Create node map for reference
    node_map = {node.id: node for node in diagram.nodes}
    
    # Generate nodes and flows
    processed_nodes = set()
    
    # Start with start node
    start_nodes = [n for n in diagram.nodes if n.node_type == "start"]
    if start_nodes:
        start_node = start_nodes[0]
        lines.append("start")
        processed_nodes.add(start_node.id)
        
        # Process flows from start
        _process_flows_from_node(start_node.id, lines, diagram.flows, node_map, processed_nodes)
    
    lines.append("@enduml")
    return "\n".join(lines)


def _process_flows_from_node(node_id: int, lines: list, flows: list, node_map: dict, processed_nodes: set):
    """Recursively process flows from a given node"""
    
    outgoing_flows = [f for f in flows if f.source_id == node_id]
    
    for flow in outgoing_flows:
        target_node = node_map[flow.target_id]
        
        if target_node.id not in processed_nodes:
            processed_nodes.add(target_node.id)
            
            # Add flow condition if present
            if flow.condition:
                lines.append(f"note right : {flow.condition}")
            
            # Generate target node based on type
            if target_node.node_type == "action":
                lines.append(f":{target_node.name};")
            elif target_node.node_type == "decision":
                condition = target_node.condition or "condition"
                lines.append(f"if ({condition}) then (yes)")
                # Handle decision branches
                _handle_decision_branches(target_node.id, lines, flows, node_map, processed_nodes)
                lines.append("endif")
            elif target_node.node_type == "fork":
                lines.append("fork")
                _handle_fork_branches(target_node.id, lines, flows, node_map, processed_nodes)
                lines.append("end fork")
            elif target_node.node_type == "merge":
                lines.append("# Merge point")
            elif target_node.node_type == "join":
                lines.append("# Join point")
            elif target_node.node_type == "end":
                lines.append("stop")
            
            # Continue processing from this node (if not end)
            if target_node.node_type not in ["end", "decision", "fork"]:
                _process_flows_from_node(target_node.id, lines, flows, node_map, processed_nodes)


def _handle_decision_branches(decision_node_id: int, lines: list, flows: list, node_map: dict, processed_nodes: set):
    """Handle decision node branches"""
    
    outgoing_flows = [f for f in flows if f.source_id == decision_node_id]
    
    for i, flow in enumerate(outgoing_flows):
        if i > 0:
            condition_label = flow.condition or "no"
            lines.append(f"elseif ({condition_label}) then")
        
        target_node = node_map[flow.target_id]
        if target_node.id not in processed_nodes:
            processed_nodes.add(target_node.id)
            
            if target_node.node_type == "action":
                lines.append(f":{target_node.name};")
            elif target_node.node_type == "end":
                lines.append("stop")
            
            # Continue from this branch
            if target_node.node_type not in ["end"]:
                _process_flows_from_node(target_node.id, lines, flows, node_map, processed_nodes)


def _handle_fork_branches(fork_node_id: int, lines: list, flows: list, node_map: dict, processed_nodes: set):
    """Handle fork node branches"""
    
    outgoing_flows = [f for f in flows if f.source_id == fork_node_id]
    
    for i, flow in enumerate(outgoing_flows):
        if i > 0:
            lines.append("fork again")
        
        target_node = node_map[flow.target_id]
        if target_node.id not in processed_nodes:
            processed_nodes.add(target_node.id)
            
            if target_node.node_type == "action":
                lines.append(f":{target_node.name};")
            
            # Continue from this branch
            if target_node.node_type not in ["end", "join"]:
                _process_flows_from_node(target_node.id, lines, flows, node_map, processed_nodes)


def generate_plantuml_activity_collection(collection: ActivityModelCollection) -> str:
    """Generate overview of all activity diagrams in collection"""
    
    lines = ["@startuml", f"title {collection.project_name} - Activity Diagrams Overview", ""]
    
    for diagram in collection.activity_diagrams:
        lines.append(f"package \"{diagram.name}\" {{")
        lines.append(f"  note as N{diagram.id}")
        lines.append(f"    Activity Diagram: {diagram.name}")
        lines.append(f"    Nodes: {len(diagram.nodes)}")
        lines.append(f"    Flows: {len(diagram.flows)}")
        if diagram.use_case_links:
            lines.append("    Linked Use Cases:")
            for link in diagram.use_case_links:
                lines.append(f"    • UC{link.use_case_id}: {link.flow_step}")
        lines.append("  end note")
        lines.append("}")
        lines.append("")
    
    lines.append("@enduml")
    return "\n".join(lines)


# Enhanced version with swimlanes
def generate_plantuml_activity_with_swimlanes(diagram: ActivityDiagram) -> str:
    """Generate activity diagram with proper swimlane support"""
    
    lines = ["@startuml", f"title {diagram.name}", ""]
    
    # Add use case links
    if diagram.use_case_links:
        lines.append("note top")
        lines.append("**Linked Use Cases:**")
        for link in diagram.use_case_links:
            lines.append(f"• UC{link.use_case_id}: {link.flow_step}")
        lines.append("end note")
        lines.append("")
    
    # If swimlanes exist, use partition syntax
    if diagram.swimlanes:
        for swimlane in diagram.swimlanes:
            lines.append(f"partition \"{swimlane.name}\" {{")
        
        # Close partitions (simplified approach)
        for _ in diagram.swimlanes:
            lines.append("}")
    
    # Generate basic flow
    lines.append("start")
    
    # Add all action nodes in sequence (simplified)
    action_nodes = [n for n in diagram.nodes if n.node_type == "action"]
    for node in action_nodes:
        lines.append(f":{node.name};")
    
    # Add decision nodes
    decision_nodes = [n for n in diagram.nodes if n.node_type == "decision"]
    for node in decision_nodes:
        condition = node.condition or "condition"
        lines.append(f"if ({condition}) then (yes)")
        lines.append("  :continue;")
        lines.append("else (no)")
        lines.append("  :alternative;")
        lines.append("endif")
    
    lines.append("stop")
    lines.append("@enduml")
    return "\n".join(lines)


# Usage examples:
# plantuml_activity = generate_plantuml_activity(your_activity_diagram)
# plantuml_collection = generate_plantuml_activity_collection(your_collection)
# plantuml_swimlanes = generate_plantuml_activity_with_swimlanes(your_activity_diagram)

def generate_clean_usecase_diagram(diagram: UseCaseDiagram) -> str:
    """Generate optimized PlantUML with minimal line crossings"""
    
    lines = [
        "@startuml",
        f"title {diagram.name}",
        "",
        "!theme plain",
        "skinparam usecase {",
        "  BackgroundColor White",
        "  BorderColor Black",
        "}",
        "skinparam actor {",
        "  BackgroundColor White",
        "  BorderColor Black",
        "}",
        ""
    ]
    
    # Group actors by position (left/right optimization)
    primary_actors = []
    secondary_actors = []
    
    # Analyze relationships to determine actor positioning
    actor_connections = {actor.id: 0 for actor in diagram.actors}
    for rel in diagram.relationships:
        if rel.source_type == "actor":
            actor_connections[rel.source_id] += 1
        if rel.target_type == "actor":
            actor_connections[rel.target_id] += 1
    
    # Split actors for left/right placement
    sorted_actors = sorted(diagram.actors, key=lambda a: actor_connections[a.id], reverse=True)
    mid_point = len(sorted_actors) // 2
    primary_actors = sorted_actors[:mid_point] if sorted_actors else []
    secondary_actors = sorted_actors[mid_point:] if sorted_actors else []
    
    # Left actors
    if primary_actors:
        for actor in primary_actors:
            lines.append(f"actor {actor.name} as A{actor.id}")
        lines.append("")
    
    # Use case rectangle grouping
    if diagram.use_cases:
        lines.append("rectangle \"System Boundary\" {")
        for uc in diagram.use_cases:
            lines.append(f"  usecase \"{uc.name}\" as UC{uc.id}")
        lines.append("}")
        lines.append("")
    
    # Right actors  
    if secondary_actors:
        for actor in secondary_actors:
            lines.append(f"actor {actor.name} as A{actor.id}")
        lines.append("")
    
    # Relationships with optimization
    associations = []
    includes = []
    extends = []
    generalizations = []
    
    for rel in diagram.relationships:
        source = f"A{rel.source_id}" if rel.source_type == "actor" else f"UC{rel.source_id}"
        target = f"A{rel.target_id}" if rel.target_type == "actor" else f"UC{rel.target_id}"
        
        if rel.relationship_type == "association":
            associations.append(f"{source} --> {target}")
        elif rel.relationship_type == "include":
            includes.append(f"{source} ..> {target} : <<include>>")
        elif rel.relationship_type == "extend":
            extends.append(f"{source} ..> {target} : <<extend>>")
        elif rel.relationship_type == "generalization":
            generalizations.append(f"{source} --|> {target}")
    
    # Output relationships in order (associations first for clarity)
    if associations:
        lines.extend(associations)
        lines.append("")
    
    if includes:
        lines.extend(includes)
        lines.append("")
        
    if extends:
        lines.extend(extends)
        lines.append("")
        
    if generalizations:
        lines.extend(generalizations)
        lines.append("")
    
    # Layout hints for cleaner arrangement
    lines.extend([
        "!define DIRECTION top to bottom direction",
        "left to right direction",
        ""
    ])
    
    lines.append("@enduml")
    return "\n".join(lines)


def generate_ultra_clean_usecase(diagram: UseCaseDiagram) -> str:
    """Maximally clean version with strategic positioning"""
    
    lines = [
        "@startuml",
        f"title {diagram.name}",
        "",
        "left to right direction",
        "skinparam packageStyle rectangle",
        ""
    ]
    
    # Actors on left
    for actor in diagram.actors:
        lines.append(f"actor :{actor.name}: as A{actor.id}")
    lines.append("")
    
    # System boundary
    lines.append("package \"System\" {")
    for uc in diagram.use_cases:
        lines.append(f"  ({uc.name}) as UC{uc.id}")
    lines.append("}")
    lines.append("")
    
    # Clean relationships
    rel_map = {
        "association": "-->",
        "include": "..> : <<include>>", 
        "extend": "..> : <<extend>>",
        "generalization": "--|>"
    }
    
    for rel in diagram.relationships:
        source = f"A{rel.source_id}" if rel.source_type == "actor" else f"UC{rel.source_id}"
        target = f"A{rel.target_id}" if rel.target_type == "actor" else f"UC{rel.target_id}"
        arrow = rel_map[rel.relationship_type]
        lines.append(f"{source} {arrow} {target}")
    
    lines.append("@enduml")
    return "\n".join(lines)