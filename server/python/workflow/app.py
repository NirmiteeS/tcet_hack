import os
import json
import re
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Function to extract only JSON from model output
def extract_json(text):
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return "{}"  # Return empty JSON if no valid JSON is found

# Function to generate a structured workflow for a given task
def generate_workflow(task_description):
    print("Generating workflow...")

    if not task_description:
        return jsonify({"error": "Task description is missing from the request"}), 400

    try:
        # Properly formatted prompt with task description injected
        prompt = (
            f"Generate a structured workflow for the following task: {task_description}. "
            "Break down the task into well-defined phases, with each phase including:\n"
            "- A title\n"
            "- A brief description\n"
            "- Key steps (specific tasks assigned to team members mentioned in the task description, along with deadlines in YYYY-MM-DD format)\n"
            "- Expected outcomes\n\n"
            "Ensure that in each phase, the steps include specific tasks assigned to team members, each with a due date. Return the tasks seperately as well. \n\n"
            "Return a structured JSON output in the following format:\n\n"
            "{\n"
            '    "tasks": [\n'
            '        {\n'
            '            "assignee": ["Person Name"],\n'
            '            "dueDate": "YYYY-MM-DD",\n'
            '            "project": "Project Name",\n'
            '            "status": "Not started",\n'
            '            "title": "Task Title"\n'
            "        }\n"
            "    ],\n"
            '    "workflow": [\n'
            '        {\n'
            '            "title": "Phase Title",\n'
            '            "description": "Brief phase description",\n'
            '            "keySteps": [\n'
            '                {\n'
            '                    "assignee": ["Person Name"],\n'
            '                    "dueDate": "YYYY-MM-DD",\n'
            '                    "task": "Task Title"\n'
            "                }\n"
            "            ],\n"
            '            "expectedOutcomes": ["Outcome 1", "Outcome 2"]\n'
            "        }\n"
            "    ]\n"
            "}\n\n"
            "Ensure the response contains only valid JSON with no extra text."
        )

        # Generate content using Google Generative AI
        model = genai.GenerativeModel("gemini-pro")
        result = model.generate_content(prompt)

        if not result.text:
            return jsonify({"error": "No response from AI model"}), 500

        raw_output = result.text.strip()
        print("Raw model output:", raw_output)

        # Extract only JSON content
        clean_json_text = extract_json(raw_output)

        try:
            workflow_json = json.loads(clean_json_text)
            if not isinstance(workflow_json, dict) or "workflow" not in workflow_json or "tasks" not in workflow_json:
                raise ValueError("Generated output is not a valid JSON structure.")
            return jsonify(workflow_json), 200
        except json.JSONDecodeError:
            print(f"Error: Generated text is not valid JSON - {clean_json_text}")
            return jsonify({"error": "Invalid workflow format received from model"}), 500

    except Exception as e:
        print(f"Error generating workflow: {e}")
        return jsonify({"error": f"Error generating workflow: {str(e)}"}), 500

# Flask route for generating a workflow
@app.route("/generate-workflow", methods=["POST"])
def workflow_endpoint():
    data = request.json
    task_description = data.get("task")
    return generate_workflow(task_description)

# Main entry point
if __name__ == "__main__":
    app.run(debug=True, port=5001)
