from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
import sys
from typing import List, Dict
import os

# Download and load English language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Load word list
def load_word_list(file_path: str = "word_list.txt") -> set:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Convert all words to lowercase and strip whitespace
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Warning: Word list file '{file_path}' not found. Using empty set.")
        return set()

# Initialize word list
word_list = load_word_list()

app = FastAPI(
    title="Text Processing API",
    description="API to extract unique words from text and compare with word list",
    version="1.0.0"
)

class TextInput(BaseModel):
    article: str

class WordAnalysis(BaseModel):
    words: List[str]
    count: int

class WordComparison(BaseModel):
    words_not_in_list: List[str]
    count_not_in_list: int
    percentage_not_in_list: float

class ExtractWordsResponse(BaseModel):
    analysis: WordAnalysis
    comparison: WordComparison

class RootResponse(BaseModel):
    message: str
    word_list_size: int
    api_version: str

@app.post("/extract-words", response_model=ExtractWordsResponse)
async def extract_unique_words(text_input: TextInput):
    try:
        # Process the text with spaCy
        doc = nlp(text_input.article)
        
        # Extract lemmatized words (excluding punctuation and whitespace)
        lemmatized_words = [token.lemma_.lower() for token in doc 
                          if not token.is_punct and not token.is_space]
        
        # Get unique words and sort them
        unique_words = sorted(set(lemmatized_words))
        
        # Find words not in the word list
        words_not_in_list = [word for word in unique_words if word not in word_list]
        
        # Calculate percentage
        total_unique_words = len(unique_words)
        if total_unique_words > 0:
            percentage = (len(words_not_in_list) / total_unique_words) * 100
        else:
            percentage = 0
            
        return ExtractWordsResponse(
            analysis=WordAnalysis(
                words=unique_words,
                count=total_unique_words
            ),
            comparison=WordComparison(
                words_not_in_list=words_not_in_list,
                count_not_in_list=len(words_not_in_list),
                percentage_not_in_list=round(percentage, 2)
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_model=RootResponse)
async def root():
    return RootResponse(
        message="Welcome to the Text Processing API. Use POST /extract-words to process text.",
        word_list_size=len(word_list),
        api_version="1.0.0"
    )
