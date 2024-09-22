#import
from openai import OpenAI
import streamlit  as st

client =  OpenAI(api_key = st.secrets["OPENAI_API_KEY"]) # Replace with your OpenAI API key

def story_gen(prompt):
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages= [
      {'role': 'system', 
       'content': """
       You are a accomplished storyteller. You have published young adult short stories for 5 years.
       Given the topic, you can write quality fantasy stories with a closed ending.
       The story must be 100-150 words long.
       """},
      {'role': 'user', 'content': prompt}
    ],
    temperature=1.3,
    max_tokens=1000
  )
  return response.choices[0].message.content

def cover_prompt(prompt):
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages= [
      {'role': 'system', 
       'content': """
        You are tasked with generating a prompt for an AI image generator.
        A story will be given and you have to analyse and digest the contents, and extract the main elements or essence of the story.
        Write a short prompt to produce an interesting and relevant cover art for the story
       """},
      {'role': 'user', 'content': prompt}
    ],
    temperature=1,
    max_tokens=1000
  )
  return response.choices[0].message.content

def cover_art(prompt):
  response = client.images.generate(
      model= 'dall-e-3',
      prompt=prompt,
      size='1024x1024',
      quality='standard',
      n=1,
      style= 'vivid'
  )
  return response.data[0].url

def storybook(prompt):
  story = story_gen(prompt)
  cover = cover_prompt(story)
  image = cover_art(prompt)

  st.image(image)
  st.caption(cover)
  st.divider()
  st.write(story)
  
st.title("Your story Powered by AI.")
st.write("Welcome to AI Story Generator App! Our AI-powered story generator, that can take that spark and turn it into an incredible tale in just one minute.")
st.image("https://cdn.storybooks.app/ai-story.webp", width = 400)

prompt = st.text_input("Give me a story topic", placeholder = "Enter a story topic")

if st.button("Generate story"):
    storybook(prompt)