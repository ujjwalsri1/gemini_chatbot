from flask import Flask, request, jsonify
import google.generativeai as genai
import mysql.connector
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Set up API key for Gemini model
genai.configure(api_key="AIzaSyDAjN9WiI--KNg2bQ1CuGMSVKnAFWWOQSc")
model = genai.GenerativeModel("gemini-1.5-flash")

# MySQL Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="prakhars",
        database="chatbot"
    )

# Function to save chat history to the database
def save_chat_history(user_message, bot_response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_message, bot_response) VALUES (%s, %s)",
        (user_message, bot_response)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Function to get recent chat history (limited to 3 entries)
def get_chat_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_message, bot_response, timestamp FROM chat_history ORDER BY timestamp DESC LIMIT 3")
    chat_history = cursor.fetchall()
    cursor.close()
    conn.close()
    return chat_history

# Function to generate response using Gemini model
def generate_gemini_response(user_message):
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Generate response from Gemini API
    bot_response = generate_gemini_response(user_message)
    
    # Save the chat history to MySQL database
    save_chat_history(user_message, bot_response)
    
    return jsonify({'message': bot_response})

@app.route('/history', methods=['GET'])
def history():
    chat_history = get_chat_history()
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)



