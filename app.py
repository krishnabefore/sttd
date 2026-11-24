"""StudyPath — Flask server. Routes only; the logic lives in recommender.py."""
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from db import query
from recommender import LEVELS, rank_courses, assign_weeks, grade_quiz, plan_progress

BUDGETS = ('Free only', 'Paid okay', 'No preference')
EDUCATION = ('High School', '11th', '12th', 'BTech', 'BCA', 'Other')

app = Flask(__name__)
app.secret_key = 'change-me-before-deploying'


@app.route('/')
def index():
    subjects = query('SELECT name FROM subjects ORDER BY name')
    return render_template('index.html', subjects=subjects, education=EDUCATION)


@app.route('/build-plan', methods=['POST'])
def build_plan():
    name = request.form.get('name', '').strip()[:100]
    education = request.form.get('education')
    education = education if education in EDUCATION else 'Other'
    term = request.form.get('subject', '').strip()
    level = request.form.get('level')
    budget = request.form.get('budget')
    goal = request.form.get('goal', '')
    level = level if level in LEVELS else 'Beginner'
    budget = budget if budget in BUDGETS else 'No preference'
    m = re.search(r'\d+', request.form.get('time', ''))
    hpw = int(m.group()) if m and int(m.group()) > 0 else 5

    if not name:
        flash('Please tell us your name to start your plan.')
        return redirect(url_for('index'))

    subject = None
    if term:
        subject = query('SELECT * FROM subjects WHERE name LIKE %s LIMIT 1', (f'%{term}%',), one=True)
    if not subject:
        flash(f'No roadmap for "{term}" yet. Pick one of the suggested subjects.')
        return redirect(url_for('index'))

    topics = query('SELECT * FROM topics WHERE subject_id=%s ORDER BY sequence_order', (subject['subject_id'],))
    weeks = assign_weeks(topics, hpw)
    learner_id = query('INSERT INTO learners (name, education) VALUES (%s,%s)', (name, education), commit=True)
    plan_id = query(
        'INSERT INTO study_plans (learner_id, subject_id, level, goal, budget, hours_per_week) '
        'VALUES (%s,%s,%s,%s,%s,%s)',
        (learner_id, subject['subject_id'], level, goal, budget, hpw), commit=True)

    for t in topics:
        courses = query('SELECT * FROM courses WHERE topic_id=%s', (t['topic_id'],))
        for c in rank_courses(courses, level, budget, goal):
            query('INSERT INTO plan_items (plan_id, course_id, week_no) VALUES (%s,%s,%s)',
                  (plan_id, c['course_id'], weeks[t['topic_id']]), commit=True)
    return redirect(url_for('plan', plan_id=plan_id))


def load_plan(plan_id):
    """The plan row with its subject and learner, or None."""
    return query('SELECT p.*, s.name AS subject, l.name AS learner, l.education '
                 'FROM study_plans p JOIN subjects s ON s.subject_id = p.subject_id '
                 'JOIN learners l ON l.learner_id = p.learner_id WHERE p.plan_id=%s', (plan_id,), one=True)


@app.route('/plan/<int:plan_id>')
def plan(plan_id):
    p = load_plan(plan_id)
    if not p:
        return redirect(url_for('index'))
    sid = p['subject_id']

    topic_rows = query('SELECT * FROM topics WHERE subject_id=%s ORDER BY sequence_order', (sid,))
    weeks = assign_weeks(topic_rows, p['hours_per_week'])

    course_rows = query('SELECT i.item_id, i.done, c.topic_id, c.title, c.platform, c.url, c.rating, '
                        'c.is_free, c.price_label FROM plan_items i '
                        'JOIN courses c ON c.course_id = i.course_id '
                        'WHERE i.plan_id=%s ORDER BY i.item_id', (plan_id,))
    question_rows = query('SELECT q.* FROM questions q JOIN topics t ON t.topic_id = q.topic_id '
                          'WHERE t.subject_id=%s ORDER BY q.question_id', (sid,))
    quiz_counts = {r['topic_id']: r['n'] for r in query(
        'SELECT topic_id, COUNT(*) AS n FROM quiz_questions '
        'WHERE topic_id IN (SELECT topic_id FROM topics WHERE subject_id=%s) GROUP BY topic_id', (sid,))}
    progress = {r['topic_id']: r for r in query('SELECT * FROM topic_progress WHERE plan_id=%s', (plan_id,))}

    topics = []
    for t in topic_rows:
        tid = t['topic_id']
        topics.append({
            'topic_id': tid, 'name': t['name'], 'week': weeks[tid], 'hours': t['est_hours'],
            'courses': [c for c in course_rows if c['topic_id'] == tid],
            'questions': [q for q in question_rows if q['topic_id'] == tid],
            'has_quiz': quiz_counts.get(tid, 0) > 0,
            'progress': progress.get(tid),
        })

    # Only topics that have a quiz can be completed, so only they count.
    quiz_topics = [t for t in topics if t['has_quiz']]
    passed = sum(1 for t in quiz_topics if t['progress'] and t['progress']['passed'])
    prog = plan_progress(passed, len(quiz_topics))
    return render_template('dashboard.html', plan=p, topics=topics, prog=prog)


@app.route('/plan/<int:plan_id>/quiz/<int:topic_id>', methods=['GET', 'POST'])
def quiz(plan_id, topic_id):
    p = load_plan(plan_id)
    if not p:
        return redirect(url_for('index'))
    topic = query('SELECT * FROM topics WHERE topic_id=%s AND subject_id=%s',
                  (topic_id, p['subject_id']), one=True)
    questions = query('SELECT * FROM quiz_questions WHERE topic_id=%s ORDER BY quiz_id', (topic_id,)) if topic else []
    if not questions:
        return redirect(url_for('plan', plan_id=plan_id))

    if request.method == 'GET':
        return render_template('quiz.html', plan=p, topic=topic, questions=questions, result=None, review={})

    answers = {q['quiz_id']: request.form.get(f"q_{q['quiz_id']}") for q in questions}
    result = grade_quiz(questions, answers)
    # Keep the best score; once a topic is passed it stays passed.
    query('INSERT INTO topic_progress (plan_id, topic_id, best_score, passed, completed_at) '
          'VALUES (%s,%s,%s,%s, IF(%s, NOW(), NULL)) '
          'ON DUPLICATE KEY UPDATE '
          'best_score = GREATEST(best_score, VALUES(best_score)), '
          'completed_at = IF(completed_at IS NULL AND VALUES(passed), NOW(), completed_at), '
          'passed = (passed OR VALUES(passed))',
          (plan_id, topic_id, result['percent'], int(result['passed']), int(result['passed'])), commit=True)
    review = {r['quiz_id']: r for r in result['review']}
    return render_template('quiz.html', plan=p, topic=topic, questions=questions, result=result, review=review)


@app.route('/api/items/<int:item_id>/toggle', methods=['POST'])
def toggle(item_id):
    if not query('SELECT item_id FROM plan_items WHERE item_id=%s', (item_id,), one=True):
        return jsonify(error='not found'), 404
    query('UPDATE plan_items SET done = NOT done WHERE item_id=%s', (item_id,), commit=True)
    item = query('SELECT done FROM plan_items WHERE item_id=%s', (item_id,), one=True)
    return jsonify(done=bool(item['done']))


if __name__ == '__main__':
    app.run(debug=True)
