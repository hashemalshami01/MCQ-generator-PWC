#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import openai
import time

# Assigning Api key
openai.api_key = "Insert API key here"

def generate_questions(topic):
    try:
        # Use OpenAI Completion API to create questions based on the user's selected topic
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate multiple choice questions on the topic: {topic}",
            max_tokens=150,
            n=5,
            stop=None,
            temperature=0.7
        )

        # Checking for errors in api
        if 'error' in response:
            raise openai.error.OpenAIError(response['error']['message'])

        # Extracting questions from the API's response
        questions = [choice['text'].strip() for choice in response['choices']]

        return questions

    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API error: {e}")
        return []

def get_correct_answers(questions):
    try:
        # Use API to generate the correct answers
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="\n".join(questions),
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.0
        )

        # Check for  errors in api
        if 'error' in response:
            raise openai.error.OpenAIError(response['error']['message'])

        # Extract the generated answer
        correct_answers = response['choices'][0]['text'].strip().splitlines()

        return correct_answers

    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API error: {e}")
        return []

def quiz_app():
    st.set_page_config(  
        page_title="MCQ Quiz PWC",
        page_icon="🧠",
        layout="wide",
    )

    st.title("MCQ Quiz PWC")

    # Get the user's topic choice
    topic = st.text_input("Enter a topic of your choice:")

    if st.button("Start Generating"):
        if topic:
            # Generate questions based on the user's topic
            questions = generate_questions(topic)

            if not questions:
                st.warning("Failed to generate questions. Please check your input and try again.")
                return

            # Fetch correct answers based on generated questions
            correct_answers = get_correct_answers(questions)

            # Initialize session state if not present
            if 'answers' not in st.session_state:
                st.session_state.answers = {}

            # Display the generated questions with options using st.form
            num_questions = min(len(questions), 5)  # Display up to 5 questions

            with st.form("quiz_form"):
                for i in range(num_questions):
                    question = questions[i]
                    options = [option.strip() for option in question.splitlines()[1:5]]
                    key = f"question_{i}"

                    # Prompt to display questions
                    st.write(f"Question {i+1}: {question.splitlines()[0]}")

                    # Use a unique key for each question's selectbox to avoid conflicts
                    selected_option = st.radio(f"Select your answer for Question {i+1}:", options, key=key)

                    # Store the selected answer in session state
                    st.session_state.answers[key] = selected_option

                # Submit button outside the loop so that the page doesn't refresh, unfortunately it isnt't working
                if st.form_submit_button("Submit All Answers"):
                    # Process submitted answers
                    # Display selected answers
                    st.subheader("Your Selected Answers:")
                    for question_key, answer in st.session_state.answers.items():
                        question_number = question_key.split("_")[1]
                        st.write(f"Question {question_number}: {answer}")

                    # Display the correct answers
                    st.subheader("Correct Answers:")
                    for i, correct_answer in enumerate(correct_answers[:num_questions]):
                        st.write(f"Question {i+1}: {correct_answer}")

                    # Calculate the user's score
                    score = sum([1 for i in range(num_questions) if st.session_state.answers[f"question_{i}"] == correct_answers[i]])

                    # Display the user's score as a grade
                    grade = (score / num_questions) * 100
                    st.subheader("Your Grade:")
                    st.write(f"You scored {score}/{num_questions}. Your grade is {grade}%.")

                    # Clear session state
                    st.session_state.answers = {}

if __name__ == "__main__":
    quiz_app()

