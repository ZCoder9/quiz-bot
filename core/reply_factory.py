
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    # If there's no current question, it means we're at the welcome message
    if current_question_id is None:
        return True, ""
    
    # Validate that the answer is not empty
    if not answer or answer.strip() == "":
        return False, "Please provide an answer."
    
    # Get or initialize the answers dictionary in the session
    if "answers" not in session:
        session["answers"] = {}
    
    # Store the answer for the current question
    session["answers"][current_question_id] = answer.strip()
    
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # If current_question_id is None, start with the first question
    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1
    
    # Check if there are more questions
    if next_question_id < len(PYTHON_QUESTION_LIST):
        question_data = PYTHON_QUESTION_LIST[next_question_id]
        
        # Format the question with options
        question_text = question_data["question_text"]
        options = question_data["options"]
        
        formatted_question = f"{question_text}\n\nOptions:\n"
        for i, option in enumerate(options, 1):
            formatted_question += f"{i}. {option}\n"
        
        return formatted_question, next_question_id
    else:
        # No more questions
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    # Get the user's answers from the session
    user_answers = session.get("answers", {})
    
    # Calculate the score
    score = 0
    total_questions = len(PYTHON_QUESTION_LIST)
    
    for question_id, user_answer in user_answers.items():
        correct_answer = PYTHON_QUESTION_LIST[question_id]["answer"]
        
        # Check if the answer matches (case-insensitive comparison)
        if user_answer.strip().lower() == correct_answer.strip().lower():
            score += 1
    
    # Calculate percentage
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Generate a final message based on performance
    final_message = f"Quiz Completed!!! \n"
    final_message += f"Your Score: {score}/{total_questions} ({percentage:.1f}%)\n\n"
    
    if percentage >= 90:
        final_message += "Excellent job! You have a great knowledge of Python!"
    elif percentage >= 70:
        final_message += "Great job! You have a good understanding of Python!"
    elif percentage >= 50:
        final_message += "Good effort! Still some practicing needed and brush up your python skills!"
    else:
        final_message += "Keep learning!!! Need so much improvement in Python skills!"

    return final_message
