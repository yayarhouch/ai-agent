import json
import os
import requests
cle_llm=os.environ.get("GROQ_API")
cle_convert=os.environ.get("CONVERT_API")
msg=[]
msg.append({"role":"system","content":"you are an ai assistant"})
tools=[{
    "type":"function",
    "function":
    {
        "name":"convert_currency",
        "description":"pour convertir une devise en la devise ciblé",
        "parameters":
        {
          "type":"object",
          "properties":{
            "amount":{
                "type":"number",
                "description":"le prix a convertir"
            },
            "to_currency":{
                "type":"string",
                "description":"la devise ciblé"
            }
          },
          "required":["to_currency","amount"]
        }
    }
}]
def send_request(msg):
    try:
        response=requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {cle_llm}"},
        json={"model":"llama-3.3-70b-versatile","messages":msg,"tools":tools}
    )
        return response
    except requests.exceptions.ConnectionError:
        return "invalid URL"
def convert_currency(amount,to_currency):
    data=requests.get(
        f"https://v6.exchangerate-api.com/v6/{cle_convert}/pair/MAD/{to_currency}/{amount}",
    )
    data1=data.json()
    conversion_result=data1["conversion_result"]
    return f"{amount} MAD = {conversion_result} {to_currency}"

avaible_tools={"convert_currency":convert_currency}
while True:
    user=input("YOU : ")
    if user == "exit":break
    msg.append({"role":"user","content":user})
    while True:
        response=send_request(msg)
        if response.status_code==401:print("invalid API")
        data=response.json()
        
        choice=data["choices"][0]
        
        message=choice["message"]
        if "tool_calls" in message:
          tool=message["tool_calls"][0]
          function=tool["function"]
          name=function["name"]
          arguments=json.loads(function["arguments"])
          result=avaible_tools[name](**arguments)
          msg.append({"role":"assistant","content":None,"tool_calls":message["tool_calls"]})
          msg.append({"role":"tool","content":result,"tool_call_id":tool["id"]})
          continue
        else:
            print(message["content"])
            msg.append({"role":"assistant","content":message["content"]})
            break
                       