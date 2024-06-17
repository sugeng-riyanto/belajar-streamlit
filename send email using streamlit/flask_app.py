from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'emails.db'

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/api/emails', methods=['GET'])
def get_emails():
    emails = query_db('SELECT * FROM emails')
    return jsonify(emails)

@app.route('/api/emails', methods=['POST'])
def add_email():
    data = request.json
    query_db('INSERT INTO emails (name, email, fee, virtual_account) VALUES (?, ?, ?, ?)', 
             [data['name'], data['email'], data['fee'], data['virtual_account']])
    return jsonify({"message": "Email added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)
