"""
Chatbot routes blueprint.
"""

import os
import sys
import traceback
from pydantic import BaseModel, SecretStr
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from typing import List, Dict, Any, Union, Optional

# Initialize Groq Chat Model with correct parameters
llm = ChatGroq(
    api_key=SecretStr("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"),
    # model="deepseek-r1-distill-llama-70b",
    model="llama3-8b-8192",
)

# Request model
class ChatRequest(BaseModel):
    user_input: str

async def chat(input, user_details_dict):
    """Chat with the AI using user input and details."""
    try:
        # Define System Instructions
        # Create prompt template for chat
        prompt_template_chat = PromptTemplate(
            input_variables=["user_input", "user_details"],
            template="""You are an AI menstrual health assistant for women. Provide expert advice on health, diet, and well-being based on the user's input and details:
            
            User Input: {user_input}
            User Details: {user_details}

            Ask questions to the user to get more information about their menstrual health.
            If the user is not comfortable with answering a question, ask them to skip it.

            Tailor the response to the user's details.
            If the user is not pregnant, do not mention pregnancy or childbirth.
            If the user is pregnant, do not mention menstruation.

            At last always prescribe to the user to consult a doctor if they have any serious concerns.

            """
        )

        chat_chain = prompt_template_chat | llm

        response = await chat_chain.ainvoke({"user_input": input, "user_details": json.dumps(user_details_dict)})
        return response.content
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERROR in chat function: {str(e)}", file=sys.stderr)
        print(f"Traceback: {error_traceback}", file=sys.stderr)
        return f"An error occurred: {str(e)}"


# Define meal models - simplified to basic dictionary structure
class DayMeals(BaseModel):
    """Meals for a single day"""
    Breakfast: str
    Lunch: str
    Dinner: str


class MealPlan(BaseModel):
    """A complete weekly meal plan"""
    Monday: DayMeals
    Tuesday: DayMeals
    Wednesday: DayMeals
    Thursday: DayMeals
    Friday: DayMeals
    Saturday: DayMeals
    Sunday: DayMeals


async def generate_day_meal(day_name: str, user_details_dict: Dict[str, Any], user_message: Optional[str] = None) -> Dict[str, str]:
    """
    Generate a meal plan for a specific day based on user details.
    
    Args:
        day_name: The day of the week to generate meals for
        user_details_dict: Dictionary containing user health data
        user_message: Optional message from user with specific meal preferences
    
    Returns:
        A dictionary containing breakfast, lunch, and dinner meals
    """
    try:
        print(f"Generating meals for {day_name}...")
        
        # Create a parser for structured output
        parser = JsonOutputParser()
        
        # Define the system prompt template
        prompt_template = PromptTemplate(
            input_variables=["day", "user_details", "user_message"],
            template="""You are a nutrition expert specializing in women's health. Create a healthy meal plan for {day} considering these user details:

{user_details}

Additional preferences: {user_message}

Consider the following when creating meals:
- If the user is in their menstrual phase, include iron-rich foods
- If the user is pregnant, focus on folate, calcium, and protein
- If the user has any food allergies or restrictions, avoid those ingredients
- Include a good balance of proteins, healthy fats, and complex carbohydrates
- Keep meals practical and relatively easy to prepare

Return a JSON object with the following structure:
{{"Breakfast": "detailed breakfast description", 
  "Lunch": "detailed lunch description", 
  "Dinner": "detailed dinner description"}}

  ONLY RETURN THE JSON OBJECT, NO OTHER TEXT.
"""
        )
        
        # Create the chain
        meal_chain = prompt_template | llm | parser
        
        # Invoke the chain
        result = await meal_chain.ainvoke({
            "day": day_name,
            "user_details": json.dumps(user_details_dict),
            "user_message": user_message if user_message else "No specific preferences provided."
        })
        
        # Ensure the result has the expected structure
        if not all(key in result for key in ["Breakfast", "Lunch", "Dinner"]):
            raise ValueError("Generated meal plan missing required meal types")
        
        return result
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERROR generating {day_name} meals: {str(e)}", file=sys.stderr)
        print(f"Traceback: {error_traceback}", file=sys.stderr)
        
        # Return a fallback meal plan in case of error
        return {
            "Breakfast": f"Simple nutritious breakfast for {day_name}.",
            "Lunch": f"Balanced lunch with protein and vegetables for {day_name}.",
            "Dinner": f"Healthy dinner with lean protein and whole grains for {day_name}."
        }


async def get_meal_plan_llm(user_details_dict: Dict[str, Any], user_message: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a meal plan step by step, one day at a time.
    
    Args:
        user_details_dict: Dictionary containing user health data
        user_message: Optional message from user with specific meal preferences
    
    Returns:
        A complete meal plan as a dictionary
    """
    try:
        print("Starting step-by-step meal plan generation...")
        
        # Days of the week to generate meals for
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Initialize the meal plan structure
        meal_plan = {}
        
        # Generate meals for each day, one at a time
        for day in days:
            print(f"Step: Generating {day}'s meals...")
            
            # Generate the day's meals
            day_meals = await generate_day_meal(day, user_details_dict, user_message)
            
            # Add to the meal plan
            meal_plan[day] = day_meals
            
            print(f"Completed step: {day} added to meal plan")
        
        print("Meal plan generation completed successfully")
        return meal_plan
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"ERROR: Meal plan generation failed: {str(e)}", file=sys.stderr)
        print(f"Traceback: {error_traceback}", file=sys.stderr)
        
        # Create a basic meal plan structure in case of error
        basic_plan = {}
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            basic_plan[day] = {
                "Breakfast": "Simple breakfast with protein and fruit.",
                "Lunch": "Simple lunch with protein and vegetables.",
                "Dinner": "Simple dinner with protein and carbohydrates."
            }
        
        return {
            "error": f"Failed to generate complete meal plan: {str(e)}",
            "meal_plan": basic_plan
        }
