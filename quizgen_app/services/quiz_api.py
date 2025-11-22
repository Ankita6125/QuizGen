import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

def generate_quiz_questions(category, subcategory, num_questions=5, difficulty="Easy"):
    prompt = f"""
    You are an AI Quiz Generator. Generate {num_questions} multiple-choice questions
    for category '{category}' and subcategory '{subcategory}'.

    Each question must have 4 options (A,B,C,D), 1 correct answer, and difficulty {difficulty}.
    Return strictly JSON array like this:
    [
      {{
        "question": "...",
        "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
        "answer": "A"
      }}
    ]
    """

    try:
        completion = client.chat.completions.create(
            model="google/gemini-flash-1.5",   # ✅ verified slug
            messages=[
                {"role": "system", "content": "You are a helpful quiz generator AI."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}  # ✅ force JSON
        )

        content = completion.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print("Error generating quiz:", e)
        return []

if __name__ == "__main__":
    questions = generate_quiz_questions("Mathematics", "Algebra", num_questions=3, difficulty="Medium")
    print(json.dumps(questions, indent=4))


@csrf_exempt
def chat_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        # System prompt to restrict AI to app queries
        system_prompt = """
        You are a helpful AI assistant for QuizGen app. 
        Answer only questions related to quiz categories, 
        quiz generation, user history, or profile.
        For unrelated queries, politely respond:
        'I can only answer questions related to QuizGen app.'
        """

        try:
            completion = client.chat.completions.create(
                model="google/gemini-flash-1.5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                
            )

            content = completion.choices[0].message.content

            return JsonResponse({"response": content})

        except Exception as e:
            return JsonResponse({"response": "Sorry, I couldn't process your request."})