
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
    question = PYTHON_QUESTION_LIST[current_question_id]
    
    try:
        user_choice = int(answer.strip())
        if user_choice not in [1, 2, 3, 4]:
            return False, "Invalid option. Please choose a option number between 1 and 4."
    except ValueError:
        return False, "Invalid input. Please enter a number between 1 and 4."
    
    selected_option = question['options'][user_choice - 1]
    
    if selected_option == question['answer']:
        session[f"question_{current_question_id}_answer"] = "Correct"
        return True, "Correct answer!"
    else:
        session[f"question_{current_question_id}_answer"] = "Incorrect"
        return True, "Incorrect answer"


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id>=len(PYTHON_QUESTION_LIST)-1:
        return None, None

    question = PYTHON_QUESTION_LIST[current_question_id+1]
    question = f'''{question['question_text']}<br>
                1. {question['options'][0]}<br>
                2. {question['options'][1]}<br>
                3. {question['options'][2]}<br>
                4. {question['options'][3]}
                '''
    

    return question, current_question_id+1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0

    for question_id in range(total_questions):
        answer_status = session.get(f"question_{question_id}_answer", "Incorrect")
        if answer_status == "Correct":
            correct_answers += 1

    final_score = f"Your score: {correct_answers}/{total_questions}."

    return f"Quiz completed! {final_score} Thank you for participating!"
