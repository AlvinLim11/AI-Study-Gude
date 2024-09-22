from openai import OpenAI
import streamlit as st
from gtts import gTTS  # Text-to-Speech conversion
import os

# Initialize OpenAI client with API key from secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Replace with your OpenAI API key

st.title("AI Study Guide Generator")

# Define the initial welcome message
initial_message = {
    "role": "assistant", 
    "content": """
    Welcome to the AI Study Guide! Type in any theory or concept you need help with, and I’ll provide an explanation or summary, followed by flashcards, and additional resources to explore.
    """
}

# Initialize session state with the welcome message if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [initial_message]

# Initialize saved history session state
if "saved_histories" not in st.session_state:
    st.session_state.saved_histories = []  # Empty list to store saved chat histories

# Initialize the language selection in session state
if "language" not in st.session_state:
    st.session_state.language = "English"  # Default language

# Sidebar for saved chat histories
with st.sidebar:
    st.header("Saved Chat Histories")
    if st.session_state.saved_histories:
        for i, history in enumerate(st.session_state.saved_histories):
            with st.expander(f"History {i+1}"):
                for message in history:
                    st.write(f"**{message['role'].capitalize()}**: {message['content']}")
    else:
        st.write("No saved histories yet.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Add a language selection toggle below the welcome message, with default from session state
st.session_state.language = st.selectbox(
    "Select your language:",
    ["English", "Malay", "Chinese"],
    index=["English", "Malay", "Chinese"].index(st.session_state.language)
)

# Function to generate and save audio summary
def generate_audio(summary_text, language_code):
    # Use appropriate language code for TTS based on selection
    tts = gTTS(summary_text, lang=language_code)
    audio_file = "summary_audio.mp3"
    tts.save(audio_file)
    return audio_file

# Function to generate content in the selected language
def generate_content(prompt, language):
    # Modify system instructions based on the selected language
    if language == "English":
        language_prompt = "Please respond in English."
        tts_language_code = 'en'
    elif language == "Malay":
        language_prompt = "Please respond in Malay."
        tts_language_code = 'ms'
    else:  # Chinese
        language_prompt = "Please respond in Chinese."
        tts_language_code = 'zh'

    # Generate the note or summary
    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 
             'content': f"""
             You are a helpful AI tutor assisting students in understanding complex theories and concepts in their studies.
             Provide clear, concise, and accurate explanations or summaries for any academic topic or theory they ask about in {language}.
             Do not answer non-academic queries. 
             Limit your response to key points and avoid unnecessary details. {language_prompt}
             """},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.6,  
        max_tokens=500  # Shorter for concise summaries
    )
    summary = summary_response.choices[0].message.content

    # Generate the flashcards (Q&A)
    flashcard_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 
             'content': f"""
             Generate flashcards in Q&A format. 
             Create simple, fact-based questions about key concepts, definitions, or important points from the summary.
             Keep the answers short and to the point. {language_prompt}
             """},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.5,  
        max_tokens=300  # For concise questions and answers
    )
    flashcards = flashcard_response.choices[0].message.content

    # Generate links to additional resources like simulations or websites
    resource_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 
             'content': f"""
             Based on the concept or theory the student asks about, suggest some helpful online resources.
             These may include links to websites, online experiments, simulations, or free books relevant to their study topic. {language_prompt}
             """},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.3,  
        max_tokens=500  # For relevant resources
    )
    resources = resource_response.choices[0].message.content

    return summary, flashcards, resources, tts_language_code

# Function to process user input and generate responses
def ai_function(prompt):
    summary, flashcards, resources, tts_language_code = generate_content(prompt, st.session_state.language)

    # Generate audio from summary in selected language
    audio_file = generate_audio(summary, tts_language_code)
    
    # Display the Assistant's response
    with st.chat_message("assistant"):
        st.markdown("### Summary:")
        st.markdown(summary)

        # Display audio player for the summary
        st.markdown("### Listen to the Summary:")
        audio_path = os.path.join(os.getcwd(), audio_file)
        audio_bytes = open(audio_path, 'rb').read()
        st.audio(audio_bytes, format='audio/mp3')
        
        st.markdown("### Flashcards (Q&A):")
        st.markdown(flashcards)

        # Display additional resources
        st.markdown("### Additional Resources:")
        st.markdown(resources)
    
    # Storing the user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    # Storing the assistant's response (summary, flashcards, resources)
    st.session_state.messages.append(
        {"role": "assistant", 
         "content": f"### Summary:\n{summary}\n\n### Flashcards (Q&A):\n{flashcards}\n\n### Additional Resources:\n{resources}"
        }
    )
    
    # Show "Save History" button after a response is generated
    st.session_state.show_save_button = True

# Accept user input
prompt = st.chat_input("Type a concept or theory you need help with ...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    
    ai_function(prompt)

# Display the "Clear History" button only if there are messages beyond the initial welcome
if len(st.session_state.messages) > 1:
    if st.button("Clear History"):
        # Reset messages to contain only the initial welcome message
        st.session_state.messages = [initial_message]
        st.session_state.language = "English"  # Reset language
        
        # Remove the audio file if it exists
        audio_file = "summary_audio.mp3"
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        st.success("Audio has been cleared. Click again to clear the chat history and reset language.")

# Display the "Save History" button only if a response has been generated
if st.session_state.get("show_save_button", False):
    if st.button("Save Chat History"):
        st.session_state.saved_histories.append(st.session_state.messages.copy())
        st.success("Chat history has been saved to the sidebar.")
        # Hide the save button after saving
        st.session_state.show_save_button = False
