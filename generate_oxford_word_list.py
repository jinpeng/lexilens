import PyPDF2
import os
from typing import List, Set, Dict
import re
import argparse
import sys


def extract_word_entries_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract word entries with definitions and levels from the Oxford 3000 PDF file.
    Returns a list of word entries.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    entries: List[str] = []
    
    try:
        with open(pdf_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Process each page
            page_number = 0
            for page in pdf_reader.pages:
                page_number += 1
                # Extract text from page
                text = page.extract_text()
                print(f"Processing page {page_number}\n")
                print(text)
                print(f"end of page {page_number}\n")
                
                # Find word entries with their definitions and levels
                # Pattern matches:
                # - Word entry starts with one or more words separated by commas, these words are the different forms of the word
                # - Followed by optional definition, definition is surrounded by parentheses, multiple definitions are separated by /
                # - Followed by one or more part of speech (n., v., etc.) separated by commas or /, these are the different parts of speech of the word
                # - Part of speech values are among following:
                #    名词 (Noun) - 缩写：n.
                #    代词 (Pronoun) - 缩写：pron.
                #    动词 (Verb) - 缩写：v.
                #    形容词 (Adjective) - 缩写：adj.
                #    副词 (Adverb) - 缩写：adv.
                #    介词 (Preposition) - 缩写：prep.
                #    连词 (Conjunction) - 缩写：conj.
                #    感叹词 (Interjection) - 缩写：interj.
                #    限定词 (Determiner) - 缩写：det.
                #    助动词 (Auxiliary Verb) - 缩写：aux.
                #    情态动词 (Modal Verb) - 缩写：modal.
                #    不定冠词 (Indefinite Article) - 缩写：indefinite article
                #    定冠词 (Definite Article) - 缩写：definite article
                #    数词 (Numeral) - 缩写：number
                # - Followed by one level (A1, A2, B1, B2, C1)
                # - Word entry ends with level (A1, A2, B1, B2, C1)
                # - Word can be a single word or different words separated by commas
                # - Word followed by mandatory part of speech (n., v., etc.), part of speech can be single or multiple words separated by commas
                # - Ending with level (A1, A2, B1, B2, C1)
                pattern = r'\b(?:[a-zA-Z]+(?:,\s*[a-zA-Z]+)*)\s+(?:(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|det\.|art\.|indefinite article)(?:,\s*(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|det\.|art\.|indefinite article))*)\s+(?:A1|A2|B1|B2|C1|C2)\b'
                
                # Find all matches
                matches = re.finditer(pattern, text)
                
                # Add each match to entries list
                for match in matches:
                    entry = match.group().strip()
                    if entry:
                        # parse the entry into word, definition, and level
                        word, definition, level = entry.split(' ', 2)
                        entries.append(f"{word} {definition} {level}")
        
        # find unique definitions
        unique_definitions = set(entry.split(' ', 1)[1] for entry in entries)
        print(f"Found {len(unique_definitions)} unique definitions")

        # save unique definitions to file
        with open('unique_definitions.txt', 'w', encoding='utf-8') as file:
            for definition in unique_definitions:
                file.write(definition + '\n')

        # sort entries alphabetically by word, ignoring case
        entries.sort(key=lambda x: x.split(' ')[0].lower())
                
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise

    return entries

def save_entries_to_file(entries: List[str], output_path: str) -> None:
    """
    Save word entries to a text file, one entry per line.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            # Sort entries alphabetically
            sorted_entries = sorted(entries)
            # Write each entry on a new line
            file.write('\n'.join(sorted_entries))
        print(f"Successfully saved {len(entries)} entries to {output_path}")
    except Exception as e:
        print(f"Error saving entries to file: {str(e)}")
        raise

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Extract word entries from Oxford 3000 PDF and save to text file'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input PDF file'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to the output text file'
    )
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Extract word entries from PDF
        print(f"Extracting word entries from {args.input}...")
        entries = extract_word_entries_from_pdf(args.input)
        
        # Save entries to file
        print(f"Found {len(entries)} word entries")
        save_entries_to_file(entries, args.output)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
