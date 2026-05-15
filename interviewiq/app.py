import os
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def build_prompt(job_title: str) -> str:
    return f"""You are an experienced hiring manager and people operations expert.

Generate exactly 3 thoughtful interview questions for a "{job_title}" role.

Each question must:
- Be specific to the actual responsibilities and challenges of this role
- Reveal how the candidate thinks, handles real situations, or approaches problems — not just what they know
- Be behavioural or situational in nature (avoid trivia or definition-based questions)

If it is not an actual explicit job title, return a polite message indicating that you cannot generate questions for that input.

Return your response as a JSON array of 3 strings, and nothing else. No explanation, no preamble. Example format:
["Question one here", "Question two here", "Question three here"]"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_questions():
    data = request.get_json()
    job_title = data.get("jobTitle", "").strip()

    if not job_title:
        return jsonify({"error": "Job title is required"}), 400

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(build_prompt(job_title))
        
        # Cleaning text, incase of any formatting issues, and parsing JSON
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(cleaned_text)

        return jsonify({"questions": questions})

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to generate questions. Please check the server logs."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
