import requests
import os
import json
cle=os.environ.get("API")
msg=[]
msg.append({"role":"system","content":"you are an ai assistant"})
tools=[{
    "type":"function",
    "function":{
        "name":"get_weather",
        "description":"trouve la temperature d une ville ",
        "parameters":
        {
            "type":"object",
            "properties":{
                "city":{
                "type":"string",
                "description":"nom de la ville"
                }
            },
            "required":["city"]
        }
    }
}
]

def send_request(msg):
    try:
        response=requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {cle}"},
        json={"model":"llama-3.3-70b-versatile","messages":msg,"tools":tools}
    )
        return response
    except requests.exceptions.ConnectionError:
        return "invalid URL"

def get_weather(city):
    return f"la temperature a {city} est 25"

available_tools = {"get_weather": get_weather}
while True:
    user = input("YOU : ")
    if user=="exit":break
    msg.append({"role": "user", "content": user})
    
    while True:  
        response = send_request(msg)
        data = response.json()
        
        choices = data["choices"]
        choice = choices[0]
        message = choice["message"]
        if "tool_calls" in message:
            tool=message["tool_calls"][0]
            function=tool["function"]
            name=function["name"]
            arguments=json.loads(function["arguments"])
            result=available_tools[name](**arguments)
            msg.append({"role":"assistant","content":None,"tool_calls":message["tool_calls"]})
            msg.append({"role":"tool","content":result,"tool_call_id":tool["id"]})
            continue
        else:
            
           print(message["content"])
           msg.append({"role": "assistant", "content": message["content"]})
           break
            
    