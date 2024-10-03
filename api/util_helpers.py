import json

def get_json_data_from_req(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None
    
def read_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None