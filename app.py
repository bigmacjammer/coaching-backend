from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/generate-advice", methods=["POST"])
def generate_advice():
    data = request.json

    prompt = f"""
You are an expert career and team coach for people managers.
Based on the following team member profile, provide:

1. Three actionable coaching tips
2. Three suggested conversation phrases for a one-on-one discussion
3. Three career growth recommendations

Team member profile:
- Name: {data['name']}
- Role: {data['role']}
- Skill Level (1-5): {data['skill_level']}
- Attitude (1-5): {data['attitude']}
- Weekly Performance Check-ins: {data['weekly_checkins']}
- Career Goals: {data['career_goals']}

Return strictly in JSON format:
{{
  "coaching_tips": [ "tip1", "tip2", "tip3" ],
  "conversation_phrases": [ "phrase1", "phrase2", "phrase3" ],
  "career_growth": [ "growth1", "growth2", "growth3" ]
}}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert team coach. Always respond strictly in JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    import json
try:
    # remove markdown code block if present
    cleaned_content = response.choices[0].message.content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(cleaned_content)
    return jsonify(parsed)
except json.JSONDecodeError:
    return jsonify({
        "raw_advice": response.choices[0].message.content,
        "error": "Could not parse JSON, returning raw text instead."
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

