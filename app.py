from flask import Flask, request, jsonify, render_template
import openai
import json
import requests


app = Flask(__name__)


api_key = ""
openai.api_key = api_key

def get_university_alpha_two_code(name, country):
    response = requests.get(f"http://universities.hipolabs.com/search?name={name}&country={country}")
    data = response.json()
    if data:
        university_data = data[0]
        return university_data.get("alpha_two_code")
    return None

def get_university_province_state(name, country):
    response = requests.get(f"http://universities.hipolabs.com/search?name={name}&country={country}")
    data = response.json()
    if data:
        university_data = data[0]
        return university_data.get("state-province")
    return None

def get_university_web_pages(name, country):
    response = requests.get(f"http://universities.hipolabs.com/search?name={name}&country={country}")
    data = response.json()
    if data:
        university_data = data[0]
        return university_data.get("web_pages")
    return None

def get_university_domains(name, country):
    response = requests.get(f"http://universities.hipolabs.com/search?name={name}&country={country}")
    data = response.json()
    if data:
        university_data = data[0]
        return university_data.get("domains")
    return None

def get_universities_in_country(country):
    response = requests.get(f"http://universities.hipolabs.com/search?country={country}")
    data = response.json()
    return data if data else None

def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "user", "content": question}
        ],
        functions=[
            {
                "name": "get_university_alpha_two_code",
                "description": "Get the alpha two code of a university by name and country",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the university"
                        },
                        "country": {
                            "type": "string",
                            "description": "The country where the university is located"
                        }
                    },
                    "required": ["name", "country"],
                },
            },
            {
                "name": "get_university_province_state",
                "description": "Get the province or state of a university by name and country",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the university"
                        },
                        "country": {
                            "type": "string",
                            "description": "The country where the university is located"
                        }
                    },
                    "required": ["name", "country"],
                },
            },
            {
                "name": "get_university_web_pages",
                "description": "Get the web pages of a university by name and country",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the university"
                        },
                        "country": {
                            "type": "string",
                            "description": "The country where the university is located"
                        }
                    },
                    "required": ["name", "country"],
                },
            },
            {
                "name": "get_university_domains",
                "description": "Get the domains of a university by name and country",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the university"
                        },
                        "country": {
                            "type": "string",
                            "description": "The country where the university is located"
                        }
                    },
                    "required": ["name", "country"],
                },
            },
            {
                "name": "get_universities_in_country",
                "description": "Get a list of universities in a specific country",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "country": {
                            "type": "string",
                            "description": "The country to retrieve the list of universities from"
                        }
                    },
                    "required": ["country"],
                },
            },
        ],
        function_call="auto"
    )
    
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']
    
    response = ask_openai(question)

    if response['choices'][0]['finish_reason'] == "function_call":
        function_call = response['choices'][0]['message']['function_call']
        arguments = json.loads(function_call['arguments'])
        
        if function_call['name'] == "get_university_alpha_two_code":
            name = arguments['name']
            country = arguments['country']
            alpha_two_code = get_university_alpha_two_code(name, country)
            answer = f"The alpha two code of {name} in {country} is {alpha_two_code}." if alpha_two_code else f"No alpha two code found for {name} in {country}."
        
        elif function_call['name'] == "get_university_province_state":
            name = arguments['name']
            country = arguments['country']
            province_state = get_university_province_state(name, country)
            answer = f"The province/state of {name} in {country} is {province_state}." if province_state else f"No province/state found for {name} in {country}."
        
        elif function_call['name'] == "get_university_web_pages":
            name = arguments['name']
            country = arguments['country']
            web_pages = get_university_web_pages(name, country)
            answer = f"The web pages of {name} in {country} are {', '.join(web_pages)}." if web_pages else f"No web pages found for {name} in {country}."
        
        elif function_call['name'] == "get_university_domains":
            name = arguments['name']
            country = arguments['country']
            domains = get_university_domains(name, country)
            answer = f"The domains of {name} in {country} are {', '.join(domains)}." if domains else f"No domains found for {name} in {country}."
        
        elif function_call['name'] == "get_universities_in_country":
            country = arguments['country']
            universities = get_universities_in_country(country)
            if universities:
                university_names = [uni["name"] for uni in universities]
                answer = f"The universities in {country} are: {', '.join(university_names)}."
            else:
                answer = f"No universities found in {country}."

        else:
            answer = "Function call not recognized."
    else:
        answer = response['choices'][0]['message']['content']

    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
