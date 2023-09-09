import json

def beautify_json(data):
    """
    Beautifies JSON data by adding indentation for improved readability.
    
    Args:
        data (str): The JSON data to be beautified.
        
    Returns:
        str: Beautified JSON data.
    """
    # Parse the JSON data into a Python dictionary
    data_dict = json.loads(data)

    # Convert the dictionary back to JSON with indentation for readability
    beautified_json = json.dumps(data_dict, indent=4)

    # Return the beautified JSON
    return beautified_json
