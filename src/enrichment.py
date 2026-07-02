import os
from typing import Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError
from src.config import GEMINI_API_KEY

class NoteEnrichment(BaseModel):
    """
    Following fields are needed in the schema:
    title, summary, category, status, effort, value, tags, technologies, next_actions
    """
    title: str = Field(
        description = "Unique, descriptive and concise title for the note derived from the content."
    )
    summary: str = Field(
        description = "Concise summary of the note in 1-2 sentences."
    )
    category: str = Field(
        description = "A broad category for the project. examples: 'AI/ML', 'Web Development', 'Mobile Development', 'Data Science', 'Cloud Computing', 'Blockchain', 'Internet of Things', 'Cybersecurity', 'DevOps', 'Game Development', 'Augmented Reality/Virtual Reality'"
    )
    status: Literal["Captured", "Clarified", "Researched", "Validated", "Started", "In Progress", "Completed", "Archived"] = Field(
        default="Captured",
        description="The current state of the idea in its lifecycle."
    )
    effort: str = Field(
        description = "The estimated effort required to complete the project. examples: 'Low', 'Medium', 'High', 'Very High'"
    )
    value: str = Field(
        description = "The value of the project to the user. examples: 'Low', 'Medium', 'High', 'Very High'"
    )
    tags: list[str] = Field(
        description = "A list of tags relevant to the project. which helps in categorizing and searching. examples: 'AI/ML', 'Web Development', 'Mobile Development', 'Data Science', 'Cloud Computing', 'Blockchain', 'Internet of Things', 'Cybersecurity', 'DevOps', 'Game Development', 'Augmented Reality/Virtual Reality'"
    )
    technologies: list[str] = Field(
        description = "Technologies needed to implement the project . examples: 'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue', 'Node.js', 'Express.js', 'Django', 'Flask', 'Spring', 'MySQL', 'PostgreSQL', 'MongoDB', 'Firebase', 'AWS', 'Azure', 'GCP'"
    )
    next_actions: list[str] = Field(
        description = "A list of next actions to be taken to implement the project. examples: 'Create a plan for the project.', 'Create a prototype for the project.', 'Create a production-ready version of the project.', 'Deploy the project.'"
    )

def enrich_note(raw_content: str, existing_titles: list[str]) -> NoteEnrichment:
    
    client = genai.Client(api_key = GEMINI_API_KEY)
    prompt = f"""
    You are an expert idea-capture assistant. Your job is to enrich raw, potentially messy voice dictation transcripts into structured note metadata.
    
    Here is the raw dictation text:
    ---
    {raw_content}
    ---
    
    Tasks:
    1. Parse and extract key details into the requested schema fields.
    2. Ensure the generated 'title' is unique and does not conflict with any of the existing titles in the vault.
    
    Existing Titles to avoid:
    {existing_titles}
    """
    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = prompt,
        config = types.GenerateContentConfig(
                response_mime_type = "application/json",
            response_schema = NoteEnrichment,
            temperature = 0.2,
        ),
    )
    return NoteEnrichment.model_validate_json(response.text)