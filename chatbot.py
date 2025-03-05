import os
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

groq_api_key = "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"


# Initialize Groq Chat Model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")

# Define System Instructions
system_message = SystemMessage(content="You are an AI health assistant for women, providing expert advice on health, diet, and well-being.")

# Request model
class ChatRequest(BaseModel):
    user_input: str

async def chat(input):
    messages = [system_message, HumanMessage(content=input)]
    response = llm.invoke(messages)
    return response


prompt_template_meal = PromptTemplate(
    input_variables=['age', 'weight', 'height', 'veg_or_nonveg', 'disease', 'region', 'allergics'],
    template='''You are a meal planning assistant. Generate a structured 7-day meal plan in JSON format based on the user's details:
    
    - Age: {age}
    - Weight: {weight}
    - Height: {height}
    - Dietary Preference: {veg_or_nonveg}
    - Health Conditions: {disease}
    - Region: {region}
    - Allergies: {allergics}

    The JSON output should be structured like this:
    {{
      "Monday": {{
        "Breakfast": [{{"meal": "Meal Name", "nutritional_value": "Calories, Proteins, etc."}}],
        "Lunch": [{{"meal": "Meal Name", "nutritional_value": "Calories, Proteins, etc."}}],
        "Dinner": [{{"meal": "Meal Name", "nutritional_value": "Calories, Proteins, etc."}}]
      }},
      "Tuesday": {{ ... }},
      ...
      "Sunday": {{ ... }}
    }}

    Ensure all values are correctly formatted and realistic.
    and make sure that eggs are considered non-veg.
    '''
)

def get_meal_plan(age, weight, height, veg_or_nonveg, disease, region, allergics):
    """
    Fetches a personalized meal plan based on user health data using Groq API.
    """
    chain_meal = LLMChain(llm=llm, prompt=prompt_template_meal)

    input_data = {
        'age': age,
        'weight': weight,
        'height': height,
        'veg_or_nonveg': veg_or_nonveg,
        'disease': disease,
        'region': region,
        'allergics': allergics
    }

    results = chain_meal.run(input_data)
    
    return results 
