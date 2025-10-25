import json
import asyncio


def get_windows_handle(result):

    # import pdb; pdb.set_trace()
    window_handle = None
    
    # assume 'result' is your CallToolResult object
    raw_text = result.content[0].text   # get the text inside TextContent

    # parse the string as JSON
    outer_json = json.loads(raw_text)

    # inside that JSON, find the "resource" entry
    content_items = outer_json.get("content", [])
    resource = next((c for c in content_items if c.get("type") == "resource"), None)

    if resource:
        blob_str = resource["resource"]["blob"]
        blob_data = json.loads(blob_str)
        window_handle = blob_data["window_handle"]
        print("Window handle:", window_handle)
        return {"window_handle": window_handle}
    else:
        print("No resource found.")
        return {"window_handle": None}
    
def get_tool_descriptions(tools):
    """
    Given a list of tool objects, return a list of their descriptions.
    
    Args:
        tools (list): A list of tool objects, each having a 'description' attribute.
    """
    try:
        tools_description = []
        for i, tool in enumerate(tools):
            try:
                # Get tool properties
                params = tool.inputSchema
                desc = getattr(tool, 'description', 'No description available')
                name = getattr(tool, 'name', f'tool_{i}')
                
                # Format the input schema in a more readable way
                if 'properties' in params:
                    param_details = []
                    for param_name, param_info in params['properties'].items():
                        param_type = param_info.get('type', 'unknown')
                        param_details.append(f"{param_name}: {param_type}")
                    params_str = ', '.join(param_details)
                else:
                    params_str = 'no parameters'

                tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                tools_description.append(tool_desc)
                print(f"Added description for tool: {tool_desc}")
            except Exception as e:
                print(f"Error processing tool {i}: {e}")
                tools_description.append(f"{i+1}. Error processing tool")

        tools_description = "\n".join(tools_description)
        print("Successfully created tools description")
    except Exception as e:
        print(f"Error creating tools description: {e}")
        tools_description = "Error loading tools"

    return tools_description

def transform_parameters(tools, func_name, params):
    """
    Transform the parameters dictionary to match the expected function arguments.
    
    Args:
        params (dict): The original parameters dictionary.
    """

    # Find the matching tool to get its input schema
    tool = next((t for t in tools if t.name == func_name), None)
    if not tool:
        print(f"DEBUG: Available tools: {[t.name for t in tools]}")
        raise ValueError(f"Unknown tool: {func_name}")

    print(f"DEBUG: Found tool: {tool.name}")
    print(f"DEBUG: Tool schema: {tool.inputSchema}")

    # Prepare arguments according to the tool's input schema
    arguments = {}
    schema_properties = tool.inputSchema.get('properties', {})
    print(f"DEBUG: Schema properties: {schema_properties}")

    for param_name, param_info in schema_properties.items():
        if not params:  # Check if we have enough parameters
            raise ValueError(f"Not enough parameters provided for {func_name}")
            
        value = params.pop(0)  # Get and remove the first parameter
        param_type = param_info.get('type', 'string')
        
        print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
        
        # Convert the value to the correct type based on the schema
        if param_type == 'integer':
            arguments[param_name] = int(value)
        elif param_type == 'number':
            arguments[param_name] = float(value)
        elif param_type == 'array':
            # Handle array input
            if isinstance(value, str):
                value = value.strip('[]').split(',')
            arguments[param_name] = [int(x.strip()) for x in value]
        else:
            arguments[param_name] = str(value)

    return arguments

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise
