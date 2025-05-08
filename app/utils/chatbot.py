"""
Chatbot routes blueprint.
"""

import os
from pydantic import BaseModel, SecretStr
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from typing import List, Dict, Any

# Initialize Groq Chat Model with correct parameters
llm = ChatGroq(
    api_key=SecretStr("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"),
    model="llama3-8b-8192",
)



# Request model
class ChatRequest(BaseModel):
    user_input: str


async def chat(input, user_details_dict):
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

    response = chat_chain.invoke({"user_input": input, "user_details": json.dumps(user_details_dict)})
    return response.content


# Define meal plan models
class Meal(BaseModel):
    """A single meal with nutritional information"""
    meal: str
    nutritional_value: str


class DayMeals(BaseModel):
    """Meals for a single day"""
    Breakfast: Meal
    Lunch: Meal
    Dinner: Meal


class MealPlan(BaseModel):
    """A complete weekly meal plan"""
    Monday: DayMeals
    Tuesday: DayMeals
    Wednesday: DayMeals
    Thursday: DayMeals
    Friday: DayMeals
    Saturday: DayMeals
    Sunday: DayMeals


async def get_meal_plan(user_details_dict):
    """
    Fetches a personalized meal plan based on user health data using Groq API.
    """
    try:
        # Create JSON parser with the MealPlan schema
        parser = JsonOutputParser(pydantic_object=MealPlan)

        # Create prompt template with format instructions
        prompt_template_meal = PromptTemplate(
            input_variables=["user_details"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
            template="""You are a meal planning assistant for a woman. Generate a structured 7-day meal plan in JSON format based on the user's details:
            
            {user_details}

            The JSON output should be structured like this:
            {format_instructions}

            Ensure all values are correctly formatted and realistic.
            Make sure that eggs are considered non-veg.
            """,
        )

        # Create the chain using the | operator
        chain = prompt_template_meal | llm.with_structured_output(MealPlan)

        # Invoke the chain with user details
        response = chain.invoke({"user_details": json.dumps(user_details_dict)})

        # Return the meal plan
        return response
    except json.JSONDecodeError:
        return {"error": "Failed to parse meal plan response"}
    except Exception as e:
        return {"error": str(e)}
