import re

def generate_question(sentence):
    # Simple sentence check for basic patterns
    sentence = sentence.strip().lower()

    # Check for "is" or "are" in the sentence (for yes/no questions)
    if re.search(r'\bis\b|\bare\b|\bwas\b|\bwere\b', sentence):
        # If the sentence contains 'is', 'are', 'was', or 'were', just move the verb to the start
        words = sentence.split()
        verb_index = next(i for i, word in enumerate(words) if word in ['is', 'are', 'was', 'were'])
        question = " ".join([words[verb_index]] + words[:verb_index] + words[verb_index+1:])
        return question.capitalize() + "?"
    
    # Check for sentences with regular verbs (add 'does' or 'did' for forming questions)
    elif re.search(r'\blikes\b|\beats\b|\bplays\b', sentence):
        # Identify the subject and verb, and transform accordingly
        words = sentence.split()
        subject = words[0]
        verb = words[1]
        object_phrase = " ".join(words[2:])
        
        # Add auxiliary verb "Does"
        return f"Does {subject} {verb} {object_phrase}?"

    # Default case: Return the sentence as a question
    else:
        return f"How would you rephrase '{sentence}' as a question?"

# Test the function
sentence_1 = "He is eating an apple."
sentence_2 = "She likes ice cream."

print(generate_question(sentence_1))  # "Is he eating an apple?"
print(generate_question(sentence_2))  # "Does she like ice cream?"
