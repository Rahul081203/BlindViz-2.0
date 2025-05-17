import requests
import streamlit as st

# def get_openai_response(input_text):
#     response = requests.post("http://localhost:8000/essay/invoke", json={"input": {"topic": input_text}})
#     return response.json().get('output', {}).get('content', "No response received.")

def get_ollama_response(input_text):
    response = requests.post("http://192.168.1.9:5500/query/invoke", json={"input": {"query": input_text}})
    
    print("Response type:", type(response.text))
    print("Response content:", response.text)
    
    try:
        json_response = response.json()
        return response.json().get('output')
    except ValueError:
        return f"Failed to decode JSON. Response content was: {response.text}"



st.title('Simple Chatbot')

# input_text = st.text_input("Enter a topic for the essay:")
input_text1 = st.text_input("Enter query: ")

# if input_text:
#     st.write(get_openai_response(input_text))

if input_text1:
    st.write(get_ollama_response(input_text1))
