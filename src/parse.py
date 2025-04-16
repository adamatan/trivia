import re
import os

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract title
    title_match = re.search(r'# (.*?)\n', content)
    title = title_match.group(1) if title_match else "Unknown Topic"

    # Extract questions and answers sections
    questions_section = re.search(r'## Questions\n(.*?)\n## Answers', content, re.DOTALL)
    answers_section = re.search(r'## Answers\n(.*)', content, re.DOTALL)

    if not questions_section or not answers_section:
        raise ValueError("Markdown file does not contain the expected structure.")

    # Extract numbered lists of questions and answers
    questions = re.findall(r'\d+\.\s+(.*)', questions_section.group(1))
    answers = re.findall(r'\d+\.\s+(.*)', answers_section.group(1))

    if len(questions) != len(answers):
        raise ValueError("The number of questions and answers do not match.")

    return title, list(zip(questions, answers))

def generate_html_for_topic(title, qa_pairs, topic_id):
    html_content = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{title} - Trivia App</title>
    <link href="https://fonts.googleapis.com/css2?family=Alef&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.5.0/font/bootstrap-icons.min.css">
    <style>
        body {{
            font-family: 'Alef', sans-serif;
            direction: rtl;
            text-align: center;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
        }}
        .container {{
            max-width: 600px;
            height: 300px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }}
        .question-number {{
            font-size: 24px;
            color: #000;
        }}
        .question-text {{
            font-size: 20px;
            margin: 20px 0;
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
        }}
        .answer-text {{
            font-size: 20px;
            margin: 20px 0;
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9b59b6; /* Purple shade */
        }}
        .button {{
            display: inline-block;
            margin: 5px;
            padding: 10px 20px;
            font-size: 16px;
            color: #007bff;
            border: 2px solid #007bff;
            background-color: transparent;
            cursor: pointer;
            transition: background-color 0.3s, color 0.3s;
        }}
        .button:hover {{
            background-color: #007bff;
            color: #fff;
        }}
        .answer {{
            display: none;
        }}
        .nav-icon {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            cursor: pointer;
            color: #000;
        }}
        .nav-icon:hover {{
            color: #007bff;
        }}
        .nav-left {{
            right: 10px;
        }}
        .nav-right {{
            left: 10px;
        }}
        .progress-bar {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }}
        .progress-icon {{
            font-size: 20px;
            margin: 0 5px;
            color: #ccc; /* Gray for unanswered */
        }}
        .progress-icon.correct {{
            color: #28a745; /* Green for correct */
        }}
        .progress-icon.wrong {{
            color: #dc3545; /* Red for wrong */
        }}
        .progress-icon.active {{
            color: #007bff; /* Blue for active */
        }}
    </style>
</head>
<body>
    <div class="container" id="trivia-app">
"""

    for i, (question, answer) in enumerate(qa_pairs):
        html_content += f"""
        <div class="question" id="question-{i}" style="display: {'block' if i == 0 else 'none'};">
            <div class="question-number">{i + 1}/{len(qa_pairs)}</div>
            <div class="question-text">{question}</div>
            <button class="button" id="show-answer-{i}" onclick="revealAnswer({i})">תשובה</button>
            <div class="answer" id="answer-{i}">
                <div class="answer-text">{answer}</div>
                <button class="button" onclick="recordAnswer({i}, true)">נכון</button>
                <button class="button" onclick="recordAnswer({i}, false)">לא נכון</button>
            </div>
            <i class="bi bi-arrow-right-circle nav-icon nav-left" onclick="prevQuestion({i})"></i>
            <i class="bi bi-arrow-left-circle nav-icon nav-right" onclick="nextQuestion({i})"></i>
        </div>
"""

    html_content += """
    </div>
    <div class="progress-bar">
"""

    for i in range(len(qa_pairs)):
        html_content += f"""
        <i class="bi bi-circle-fill progress-icon" id="progress-{i}"></i>
"""

    html_content += f"""
    </div>
    <div id="result" style="display:none;">
        <h2>תוצאה</h2>
        <p id="score"></p>
        <button class="button" onclick="window.location.href='index.html'">חזור לדף הראשי</button>
    </div>
    <script>
        let correctAnswers = 0;
        let currentQuestion = 0;
        const totalQuestions = """ + str(len(qa_pairs)) + """;

        function revealAnswer(index) {
            document.getElementById('answer-' + index).style.display = 'block';
            document.getElementById('show-answer-' + index).style.display = 'none';
        }

        function recordAnswer(index, isCorrect) {
            if (isCorrect) {
                correctAnswers++;
                document.getElementById('progress-' + index).classList.add('correct');
            } else {
                document.getElementById('progress-' + index).classList.add('wrong');
            }
            nextQuestion(index);
        }

        function nextQuestion(index) {
            document.getElementById('question-' + index).style.display = 'none';
            document.getElementById('progress-' + index).classList.remove('active');
            currentQuestion++;
            if (currentQuestion < totalQuestions) {
                document.getElementById('question-' + currentQuestion).style.display = 'block';
                document.getElementById('progress-' + currentQuestion).classList.add('active');
            } else {
                showResult();
            }
        }

        function prevQuestion(index) {
            if (index > 0) {
                document.getElementById('question-' + index).style.display = 'none';
                document.getElementById('progress-' + index).classList.remove('active');
                currentQuestion--;
                document.getElementById('question-' + currentQuestion).style.display = 'block';
                document.getElementById('progress-' + currentQuestion).classList.add('active');
            }
        }

        function showResult() {
            document.getElementById('trivia-app').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            document.getElementById('score').innerText = 'ענית נכון על ' + correctAnswers + ' מתוך ' + totalQuestions + ' שאלות.';
        }

        // Initialize the first question as active
        document.getElementById('progress-0').classList.add('active');
    </script>
</body>
</html>
"""
    return html_content

def generate_index_html(titles):
    html_content = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Trivia Topics</title>
    <link href="https://fonts.googleapis.com/css2?family=Alef&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Alef', sans-serif;
            direction: rtl;
            text-align: center;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .topic {
            font-size: 20px;
            margin: 10px 0;
            color: #007bff;
            cursor: pointer;
            transition: color 0.3s;
            border: 2px solid #007bff;
            border-radius: 25px;
            padding: 10px 20px;
            display: inline-block;
            background-color: #fff; /* Default white background */
        }
        .topic:hover {
            color: #0056b3;
        }
        .topic.visited {
            background-color: #e6e6fa; /* Very light purple background for visited */
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>בחר נושא טריוויה</h1>
"""

    for i, title in enumerate(titles):
        html_content += f"""
        <div class="topic" onclick="window.location.href='topic_{i}.html'">{title}</div>
"""

    html_content += """
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const topics = document.querySelectorAll('.topic');
            topics.forEach(topic => {
                const title = topic.innerText;
                if (localStorage.getItem(title)) {
                    topic.classList.add('visited');
                }
                topic.addEventListener('click', function() {
                    localStorage.setItem(title, 'visited');
                });
            });
        });
    </script>
</body>
</html>
"""
    return html_content

def main():
    md_files = [f for f in os.listdir('.') if f.endswith('.md')]
    titles = []

    for i, md_file in enumerate(md_files):
        title, qa_pairs = parse_markdown(md_file)
        titles.append(title)
        html_content = generate_html_for_topic(title, qa_pairs, i)
        with open(f'../app/topic_{i}.html', 'w', encoding='utf-8') as file:
            file.write(html_content)

    index_html_content = generate_index_html(titles)
    with open('../app/index.html', 'w', encoding='utf-8') as file:
        file.write(index_html_content)

if __name__ == "__main__":
    main()