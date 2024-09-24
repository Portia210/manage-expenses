import configparser
import google.generativeai as genai
import os


# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config_gemini.ini')
API_KEY = config['DEFAULT']['ApiKey']
print(API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Write a story about a magic backpack.")
print(response.text)