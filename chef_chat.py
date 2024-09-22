#import
from openai import OpenAI
import streamlit  as st

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"]) # Replace with your OpenAI API key

st.title("Chef Chat (2 Star Michelin Expperience)")

def generate_content(prompt):
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages= [
      {'role': 'system', 
       'content': """
        You are a 2 michelin satr chef who wants to help home cooks improve their cooking skills.
        You may only answer home cooking related questions.
        If they ask about any nonsence outside of cooking, SCOLD THEM!
       """},
      {'role': 'user', 'content': prompt}
    ],
    temperature=1.3,
    max_tokens=1000
  )
  return response.choices[0].message.content


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", 
            "content": """
            How can i help you today?
        """}
    ]
    
#Display chat messages from history on app rerun   
for messages  in st.session_state.messages:
    with st.chat_message(messages["role"]):
        st.markdown(messages["content"])

#Process and store prompts and responses
def ai_function(prompt):
    response = generate_content(prompt)
    
    #Display the Assistant Message
    with st.chat_message("assistant"):
        st.markdown(response)
        
    #Storing the user Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    
#Accept user input
prompt = st.chat_input("Type your question or ask for help")

if  prompt:
    with  st.chat_message("user"):
        st.markdown(prompt)
        
    ai_function(prompt)

