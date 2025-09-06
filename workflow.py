from sub_graph import systemRequest

systemrequestgraph = systemRequest()

workflow =systemrequestgraph.compile()

workflow.get_graph().draw_mermaid_png(output_file_path="sub_graph.png")