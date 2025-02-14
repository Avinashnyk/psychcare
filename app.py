from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('questions'))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        answers = {
            'q1': request.form.get('q1'),
            'q2': request.form.get('q2'),
            'q3': request.form.get('q3'),
            'q4': request.form.get('q4'),
            'q5': request.form.get('q5'),
            'q6': request.form.get('q6'),
            'q7': request.form.get('q7'),
            'q8': request.form.get('q8'),
            'q9': request.form.get('q9'),
            'q10': request.form.get('q10')
        }
        session['answers'] = answers
        return redirect(url_for('results'))
    return render_template('questions.html')

@app.route('/results')
def results():
    if 'username' not in session:
        return redirect(url_for('login'))
    answers = session.get('answers', {})
    conclusion = analyze_responses(answers)
    return render_template('results.html', conclusion=conclusion)

def analyze_responses(answers):
    # Initialize scores for different categories
    happiness_score = 0
    stress_score = 0
    exercise_score = 0
    sleep_score = 0
    support_score = 0
    mindfulness_score = 0
    overwhelm_score = 0
    hobbies_score = 0
    loneliness_score = 0
    confidence_score = 0

    # Scoring logic for each question
    scores = {
        'always': 2,
        'often': 1,
        'sometimes': 0,
        'rarely': -1,
        'never': -2
    }

    # Calculate scores for each category
    happiness_score = scores.get(answers['q1'], 0)
    stress_score = scores.get(answers['q2'], 0)
    exercise_score = scores.get(answers['q3'], 0)
    sleep_score = scores.get(answers['q4'], 0)
    support_score = scores.get(answers['q5'], 0)
    mindfulness_score = scores.get(answers['q6'], 0)
    overwhelm_score = scores.get(answers['q7'], 0)
    hobbies_score = scores.get(answers['q8'], 0)
    loneliness_score = scores.get(answers['q9'], 0)
    confidence_score = scores.get(answers['q10'], 0)

    # Total score
    total_score = (
        happiness_score +
        stress_score * -1 +  # Reverse score for stress
        exercise_score +
        sleep_score +
        support_score +
        mindfulness_score +
        overwhelm_score * -1 +  # Reverse score for overwhelm
        hobbies_score +
        loneliness_score * -1 +  # Reverse score for loneliness
        confidence_score
    )

    # Detailed analysis
    analysis = []

    # Happiness
    if happiness_score >= 1:
        analysis.append("You generally feel happy, which is a great sign of emotional well-being.")
    else:
        analysis.append("You may not feel happy often. Consider activities that bring you joy or seek support.")

    # Stress
    if stress_score <= -1:
        analysis.append("You experience stress frequently. Practicing relaxation techniques or mindfulness may help.")
    else:
        analysis.append("You manage stress well, which is beneficial for your mental health.")

    # Exercise
    if exercise_score >= 1:
        analysis.append("You exercise regularly, which is excellent for both physical and mental health.")
    else:
        analysis.append("You may not exercise often. Incorporating physical activity into your routine can improve your mood.")

    # Sleep
    if sleep_score >= 1:
        analysis.append("You get enough sleep, which is crucial for mental and physical well-being.")
    else:
        analysis.append("You may not be getting enough sleep. Prioritize rest and establish a sleep routine.")

    # Support
    if support_score >= 1:
        analysis.append("You feel supported by others, which is important for emotional resilience.")
    else:
        analysis.append("You may not feel supported often. Consider reaching out to friends, family, or support groups.")

    # Mindfulness
    if mindfulness_score >= 1:
        analysis.append("You practice mindfulness or meditation, which can help reduce stress and improve focus.")
    else:
        analysis.append("You may not practice mindfulness often. Consider trying meditation or deep breathing exercises.")

    # Overwhelm
    if overwhelm_score <= -1:
        analysis.append("You often feel overwhelmed. Breaking tasks into smaller steps or seeking help may be beneficial.")
    else:
        analysis.append("You manage your responsibilities well without feeling overwhelmed.")

    # Hobbies
    if hobbies_score >= 1:
        analysis.append("You engage in hobbies or activities you enjoy, which is great for mental health.")
    else:
        analysis.append("You may not engage in hobbies often. Finding time for activities you enjoy can improve your mood.")

    # Loneliness
    if loneliness_score <= -1:
        analysis.append("You often feel lonely. Connecting with others or joining social groups may help.")
    else:
        analysis.append("You rarely feel lonely, which is a positive sign of social well-being.")

    # Confidence
    if confidence_score >= 1:
        analysis.append("You feel confident about yourself, which is important for self-esteem and mental health.")
    else:
        analysis.append("You may not feel confident often. Practicing self-compassion and setting small goals can help.")

    # Analyze descriptive answer (q11)
    descriptive_answer = answers.get('q11', '').lower()
    if descriptive_answer:
        if any(word in descriptive_answer for word in ['sad', 'lonely', 'overwhelmed', 'stressed', 'anxious']):
            analysis.append("Your description suggests you may be experiencing negative emotions. It's important to address these feelings and seek support if needed.")
        elif any(word in descriptive_answer for word in ['happy', 'joy', 'content', 'calm', 'relaxed']):
            analysis.append("Your description suggests you are in a positive emotional state. Keep up the good work!")
        else:
            analysis.append("Your description provides additional context about your feelings. Reflect on your responses and consider seeking support if needed.")

    # Overall conclusion
    if total_score >= 10:
        conclusion = "You are in a good mental and emotional state. Keep up the positive habits!"
    elif 0 <= total_score < 10:
        conclusion = "You have some positive habits, but there is room for improvement. Focus on self-care and seek support if needed."
    else:
        conclusion = "You may be struggling with your mental health. It's important to seek professional help and focus on self-care."

    # Combine detailed analysis and overall conclusion
    detailed_analysis = "<br>".join(analysis)
    final_conclusion = f"<h2>Detailed Analysis:</h2><p>{detailed_analysis}</p><h2>Overall Conclusion:</h2><p>{conclusion}</p>"
    return final_conclusion

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)