#RELEVANT IMPORTS
import pandas as pd
import openai
import json

# load api key from JSON ;) safety first
with open("openai_key.json", "r") as file:
    key = json.load(file)["api_key"]

# create client with the API key
client = openai.OpenAI(api_key=key)

# Function to call OpenAI API and get the generation from the prompt
def callOpenAI(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

# Definitions for different types of ambiguities and incompleteness
definitions = {
    "lexical_ambiguity": "Lexical ambiguity occurs when a word has multiple meanings, making its interpretation dependent on the context. It can arise in two forms: (1) when a word has unrelated meanings despite sharing the same spelling and pronunciation, it is called homonym (e.g.,bank as a financial institution vs. bank as the side of a river). These meanings originate from different etymology root (2) when a word has related meanings that stem from a single etymology, it is referred to as Polysemy (e.g.,green referring to the color and to something environmentally friendly)",
    "syntactic_ambiguity": "Syntactic ambiguity occurs when a given sequence of words can be given more than one grammatical structure, and each has a different meaning. In the terminology of compiler construction, syntactic ambiguity occurs when a sentence has more than one parse.",
    "semantic_ambiguity": "Semantic ambiguity occurs when a sentence has more than one way of reading it within its context, although it contains no lexical or syntactic ambiguity. Semantic ambiguity can be viewed as ambiguity with respect to the logical form, usually expressed in predicate logic, of a sentence.",
    "pragmatic_ambiguity": "Pragmatic ambiguity occurs when a sentence has several meanings in the context in which it is uttered. The context comprises the language context, i.e., the sentences uttered before and after, and the context beyond language, i.e., the situation, the background knowledge, and expectations of the speaker or hearer and the writer or reader.",
    "vagueness": " A statement is considered vague if it admits borderline cases. A requirement is vague if it is not clear how to measure whether the requirement is fulfilled or not.",
    "incompleteness": "Missing information and lack of details regarding different parts of the feature request."
    }

# Function to create a prompt for generation based on the ambiguity class name, original title, original request, and request number
def detection_prompt(defect_type, original_request, original_title=None):
    if original_title is None:
        original_title = "N/A"

    # request stucture
    request_statement = f"Statement: Request Number - na | Request Title - {original_title} | Request Description - {original_request}"
    definition = definitions.get(defect_type.lower(), "No definition available for this defect type.")
    definition = f"{defect_type}: {definition}"

    # Add the definition to the prompt
    prompt = f"Definition: {definition}\n\n"
    
    # Prompt for Incompleteness
    if defect_type.lower() == "incompleteness":
        prompt += f"""You are a software analyst specializing in incompleteness detection in GitHub feature requests.
        Carefully analyze the given feature request statement and determine whether it is incomplete. If the request is incomplete, identify the missing information required for completeness. Include all the missing information in a single comma-separated list. Ensure that every element of the list is enclosed in quotation marks.
        If the request statement is complete, return Missing Information: No Defect Found.
        Do not provide any explanations, reasoning, or additional text that is not from the given statement.

       Statement: {original_request} """

    # Prompt for ambiguity detection
    elif defect_type.lower() in ["lexical_ambiguity", "syntactic_ambiguity", "semantic_ambiguity", "pragmatic_ambiguity", "vagueness"]:
        subclass = defect_type.replace("_", " ").title()
        prompt += f"""You are a software analyst specializing in ambiguity detection in GitHub feature requests.
        Carefully read the given statement. Extract and list any text segments containing {subclass} ambiguity from the statement. Multiple segments may contain {subclass} ambiguity; include all of them in a single comma-separated list. Make sure to have all elements of the list in quotation marks.
        If no segments are found, return No Defect Found. Do not give any explanations, reasoning, or any extra text that is not from the given statement.
    
        Statement: {original_request}"""

    else:
        raise ValueError(f"Invalid defect_type: {defect_type}")
    
    return prompt

#CHECK THIS
# prompt for generating clarifying questions
def cqs_prompt(segment, defect_type, original_request):
    prompt = f"""You are a software requirements analyst. Given the following segment from a GitHub feature request, generate a clarifying questions to help the requester remove the {defect_type}.
    Segment: "{segment}"
    Original Request: "{original_request}"

    Only output the question. Do not explain or elaborate."""
    return prompt

defect_types = ["lexical_ambiguity", "syntactic_ambiguity", "semantic_ambiguity", "pragmatic_ambiguity", "vagueness", "incompleteness"]



def questions_for_request(original_request, original_title=None):
    results = []

    for defect_type in defect_types:
        # detecting defects in the original request
        detect_prompt = detection_prompt(defect_type, original_request, original_title)
        generation = callOpenAI(detect_prompt)
        # print the generation for debugging
        print(f"segment generation for {defect_type}:\n{generation}\n")

        for segment in generation.split(","):
            segment = segment.strip().strip('"')

            if segment.lower() != "no defect found": # if no defect found, skip to next iteration
                # question prompt
                question_prompt = cqs_prompt(segment, defect_type, original_request)
                question = callOpenAI(question_prompt)
                # print the question for debugging
                print(f"question for segment '{segment}' of defect type '{defect_type}':\n{question}\n")

                # save the results
                results.append({
                    "original_request": original_request,
                    "original_title": original_title,
                    "detect_prompt": detect_prompt,
                    "segment": segment,
                    "defect_type": defect_type,
                    "question_prompt": question_prompt,
                    "question": question
                })

    # df with the results
    df = pd.DataFrame(results)
    return df

#turns questions dataframe into a list of dictionaries
def get_questions_list(df):
    questions_list = []

    for idx, row in df.iterrows():
        questions_list.append({
            "row_index": idx,
            "question": row["question"],
            "segment": row["segment"],
            "defect_type": row["defect_type"]
        })

    return questions_list

def save_answer (df, question, answer):
    # Save the answer according to the question
    df['answer'] = df.apply(lambda row: answer if row['question'] == question else None, axis=1)
    return df
   
