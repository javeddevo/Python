from flask import Flask, render_template, request,jsonify
import yaml
app=Flask(__name__)

# Function to read YAML file
def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def parse_yaml(items):
    result = []
    for key, value in items.items():
        item = {
            "name": value.get("name"),
            "purchased_date": value.get("purchased_date"),
            "price": value.get("price"),
            "additional_data": {
                "expiration": value.get("additional_data", {}).get("expiration"),
                "dimensions": value.get("additional_data", {}).get("dimensions")
            }
        }
        result.append(item)
    return result

# Load YAML data
data = read_yaml_file("sample.yaml")

# Extract categories
edibles = data["file_info"]["orders"]["edibles"]
others = data["file_info"]["orders"]["others"]


parsed_edibles = parse_yaml(edibles)
parsed_others = parse_yaml(others)

allrecords=parsed_edibles + parsed_others

@app.route('/')
def index():
    return jsonify({"message":"Welcome to the YAML Parser"})

@app.route("/orders",methods=["GET"])
def orders():
    return jsonify(parsed_edibles)



if __name__ == "__main__":
    app.run(debug=True)


