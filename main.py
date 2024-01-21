from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import openai
import sys
import traceback
from contextlib import redirect_stdout
import io

openai.api_key = "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"
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://naveendevadi18:Naveenlm10@naveendevd.e46pwol.mongodb.net/chatgpt"
mongo = PyMongo(app)

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    myChats = [chat for chat in chats]
    print("Home Page Loaded with Chats:", myChats)
    return render_template("index.html", myChats=myChats)

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        question = request.json.get("question")
        print("Received Question:", question)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Convert this mathematical problem to Python code: {question}. Please show me only the python code for this that prints the results. Do not write anything else at the start. Do not include any explanations"}
            ]
        )
        python_code = response.choices[0].message.content
        python_code = python_code.strip('`')
        print("Generated Python Code:", python_code)

        result = None
        try:
            code_out = io.StringIO()
            with redirect_stdout(code_out):
                exec(python_code)
            result = code_out.getvalue()
        except Exception as e:
            result = f"Error executing the generated Python code: {traceback.format_exc()}"
            print("Execution Error:", result)

        data = {"question": question, "answer": result.strip()}
        print("Execution Result:", result)
        mongo.db.chats.insert_one({"question": question, "answer": result.strip()})
        return jsonify(data)

    return jsonify({"result": "Ready to receive questions."})

if __name__ == "__main__":
    app.run(debug=True, port=5001)