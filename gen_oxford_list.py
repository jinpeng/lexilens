import re
import logging

# Set up logging
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(message)s'
)


# Define defintion pattern
start_with_definition_pattern = re.compile(r'^\((.*?)\)')
definition_pattern = re.compile(r'^\((.*?)\)$')


# Define possible values for part of speech
PART_OF_SPEECH_VALUES = [
    'n\.', 'noun\.', 'v\.', 'adj\.', 'adv\.', 'prep\.', 'pron\.', 'conj\.', 'interj\.', 'det\.', 'auxiliary', 'auxiliary v\.', 'aux\.', 'exclam\.',
    'modal', 'modal v\.', 'indefinite article', 'definite article', 'number', 'infinitive marker'
]
start_with_part_of_speech_pattern = re.compile(r'^(' + '|'.join(PART_OF_SPEECH_VALUES) + ')')
part_of_speech_pattern = re.compile(r'^(' + '|'.join(PART_OF_SPEECH_VALUES) + ')$')


LEVEL_VALUES = [
    'A1', 'A2', 'B1', 'B2', 'C1', 'C2'
]
level_pattern_string = '|'.join(LEVEL_VALUES)
level_pattern = re.compile(r'(' + level_pattern_string + ')')


def parse_subentry(subentry):
    # parse the subentry
    # the subentry is a string that starts with optional definition surrounded by parentheses
    # followed by one or more part of speech, multiple part of speech are separated by comma or /
    # followed by a level (A1, A2, B1, B2, C1, C2)

    # parse the definition
    if subentry.startswith('('):
        definition = subentry.split('(')[1].split(')')[0]
        logging.debug(f'DEFINITION: {definition}')
    else:
        definition = ''
    
    # remove the definition from the subentry
    subentry = subentry.replace(f'({definition})', '').strip()

    # parse the level
    level_match = level_pattern.search(subentry)
    if level_match:
        level = level_match.group(1)
        logging.debug(f'LEVEL: {level}')
    else:
        logging.debug(f'LEVEL NOT FOUND: {subentry}')

    # remove the level from the subentry
    subentry = subentry.replace(f'{level}', '').strip()

    # parse the part of speech
    # split the subentry by comma or /
    part_of_speech = []
    part_of_speech_candidates = re.split(r',|\/', subentry)
    for part_of_speech_candidate in part_of_speech_candidates:
        part_of_speech_candidate = part_of_speech_candidate.strip()
        if part_of_speech_candidate == '':
            continue
        if part_of_speech_pattern.match(part_of_speech_candidate):
            part_of_speech.append(part_of_speech_candidate)
        else:
            logging.debug(f'PART OF SPEECH NOT MATCHED: {part_of_speech_candidate}')
    
    logging.debug(f'PART OF SPEECH: {part_of_speech}')



def parse_word_entry(line):
    logging.debug(f'-------BEGIN PARSING WORD ENTRY: {line}')
    # Word pattern:
    # - Word entry starts with one or more words separated by commas, these words are the different forms of the word
    # - Word can be a single word or different words separated by commas
    # - Word may have hyphen, e.g. 'long-term', word may have '\'', such as 'o\'clock'
    # - Word may contain one or more words separated by space, such as 'all right'
    # - To separate the word, either use '(' or part of speech

    # split the line by space
    word_parts = []
    line_parts = line.split(' ')
    line_part_index = 0
    for line_part_index in range(len(line_parts)):
        # skip the first line part, because 'number' will match part of speech
        if line_part_index == 0:
            word_parts.append(line_parts[line_part_index])
            line_part_index += 1
            continue
        remaining_line = ' '.join(line_parts[line_part_index:])
        if start_with_definition_pattern.match(remaining_line):
            # line_part before the definition is the word
            break
        elif start_with_part_of_speech_pattern.match(remaining_line):
            # line_part before the part of speech is the word
            break
        else:
            word_parts.append(line_parts[line_part_index])
        line_part_index += 1

    word = ' '.join(word_parts)
    logging.debug(f'FOUND WORD: {word}')
 
    line = line.replace(word, '').strip()
    logging.debug(f'LINE AFTER REMOVING WORD: {line}')

    # split the line into multiple subentries by level (A1, A2, B1, B2, C1, C2) followed by a comma
    # each subentry has a string followed by level (A1, A2, B1, B2, C1, C2) and a comma
    # the string can be a definition surrounded by parentheses, a part of speech that ends with a dot
    subentries = []
    subentry_candidates = re.split(r'(A1|A2|B1|B2|C1|C2),', line)
    index = 0
    subentry_part = ''
    for candidate in subentry_candidates:
        candidate = candidate.strip()
        if candidate == '':
            continue
        elif candidate == 'A1' or candidate == 'A2' or candidate == 'B1' or candidate == 'B2' or candidate == 'C1' or candidate == 'C2':
            subentry = subentry_part + ' ' + candidate
            subentries.append(subentry)
        elif candidate.endswith('A1') or candidate.endswith('A2') or candidate.endswith('B1') or candidate.endswith('B2') or candidate.endswith('C1') or candidate.endswith('C2'):
            subentry = candidate
            subentries.append(subentry)
        else:
            subentry_part = candidate
        index += 1

    for subentry in subentries:
        logging.debug(f'SUBENTRY: {subentry}')


    # parse each subentry
    for subentry in subentries:
        parse_subentry(subentry)



def find_second_line_candidates(lines):
    # find the lines that are not the first line of word entry
    # the first line of word entry starts with a word
    # the second line of word entry starts with level (A1, A2, B1, B2, C1, C2)
    # or starts with definition surrounded by parentheses
    # or starts with part of speech that ends with a dot
    second_line_pattern = re.compile(r'^(A1|A2|B1|B2|C1|C2|\([^)]*\)|[a-zA-Z]+[.])')

    second_line_candidates = [line for line in lines if second_line_pattern.match(line.strip())]

    for line in second_line_candidates:
        logging.debug(line)


def find_word_with_number(lines):
    pattern = re.compile(r'^([a-zA-Z]+\d)\s.*$')
    candidates = [line for line in lines if pattern.match(line.strip())]

    for line in candidates:
        logging.debug(line)



def main():
    # Read the input text file from rawdata/Oxford3000.txt
    with open("rawdata/Oxford3000.txt", "r") as file:
        oxford_list = file.readlines()

    for line in oxford_list:
        parse_word_entry(line)



if __name__ == "__main__":
    main()