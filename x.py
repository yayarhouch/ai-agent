import requests
import json
import os
cle_groq=os.environ.get("API_GROQ")
cle_convert=os.environ.get("API_convert")
cle_news=os.environ.get("API_news")
cle_meteo=os.environ.get("API_meteo")
msg=[]
msg.append({"role":"system","content":"you are an ai assistant"})

tools=[{
    "type":"function",
    "function":{
        "name":"convert_currency",
        "description":"pour convertir un amount en une devise demandé",
        "parameters":
        {
            "type":"object",
            "properties":{"amount":{"type":"number","description":"le amount a convertir"} , "to_currency":{"type":"string","description":"la devise ciblé"}},
            "required":["amount","to_currency"]
        }
    }
},
{
    "type":"function",
    "function":{
        "name":"get_news",
        "description":"pour avoir des information sur le query",
        "parameters":{
            "type":"object",
            "properties":{"query":{"type":"string","description":"le sujet a rechercher"}},
            "required":["query"]
        }
    }
},
{
    "type":"function",
    "function":{
        "name":"get_weather",
        "description":"pour trouver la temperature d une ville",
        "parameters":{
            "type":"object",
            "properties":{
                "lat":{
                    "type": "number",
                    "description":"coordone de la ville a rechercher"
                },
                "lon":{
                    "type":"number",
                    "description":"coordone de la ville a rechercher" 
                }
            },
            "required":["lat","lon"]
        }
    }
}
]
def get_news(query):
    try:
        datas=requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={cle_news}")
        data=datas.json()
        article1=data["articles"][0]
        article2=data["articles"][1]
        article3=data["articles"][2]
        title1=article1["title"]
        title2=article2["title"]
        title3=article3["title"]
        content1=article1["content"]
        content2=article2["content"]
        content3=article3["content"]
        return f"{title1}:{content1},{title2}:{content2},{title3}:{content3}"
    except requests.exceptions.ConnectionError:
        return "invalid url"

def get_weather(lat,lon):
    
    datas=requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={cle_meteo}"
    )
    data=datas.json()
    main=data["main"]
    temp=main["temp"]
    weather=data["weather"][0]
    description=weather["description"]
    return f"temperature is {temp} , mateo description is {description}"

def send_request(msg):
    try:
        response=requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {cle_groq}"},
        json={"model":"llama-3.3-70b-versatile","messages":msg,"tools":tools}
    )
        return response
    except requests.exceptions.ConnectionError:
        return "invalid url"
def convert_currency(amount,to_currency):
    try:
        data=requests.get(
        f"https://v6.exchangerate-api.com/v6/{cle_convert}/pair/MAD/{to_currency}/{amount}")
        if data.status_code==401:return "invalid api key"
        else:
            data1=data.json()
            conversion_result=data1["conversion_result"]
            return f"{amount} en {to_currency} est {conversion_result} {to_currency}"
    except requests.exceptions.ConnectionError:
        return "invalid url"
avaible_tools={"convert_currency":convert_currency,
               "get_news":get_news,
               "get_weather":get_weather}
while True:
    user=input("YOU : ")
    if user=="exit":break
    msg.append({"role":"user","content":user})
    while True:
        response=send_request(msg)
        if isinstance(response, str):
           print(response)
           break
        data=response.json()
       
        choices=data["choices"][0]
        message=choices["message"]
        if "tool_calls" in message:
            tool_call=message["tool_calls"][0]
            function=tool_call["function"]
            name=function["name"]
            arguments=json.loads(function["arguments"])
            result=avaible_tools[name](**arguments)
            msg.append({"role":"assistant","content":None,"tool_calls":message["tool_calls"]})
            msg.append({"role":"tool","content":result,"tool_call_id":tool_call["id"]})
            continue
        else:
            print(message["content"])
            msg.append({"role":"assistant","content":message["content"]})
            break
