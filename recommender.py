"""The 'brain': ranks courses, lays topics out week by week, and grades quizzes.
Pure Python, no database, so it is easy to test (and to swap for C++ later)."""

LEVELS = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}

PASS_MARK = 70  # percent needed on a topic quiz to complete the topic

# Which kind of course suits which goal. A small nudge, not a rule.
GOAL_PLATFORMS = {
    'Exam prep': {'Coursera', 'edX', 'Khan Academy'},      # structured, syllabus-like
    'Coursework': {'Coursera', 'edX', 'Khan Academy'},
    'Job skill': {'Udemy', 'freeCodeCamp', 'YouTube'},     # hands-on, project-based
    'Curiosity': {'YouTube', 'freeCodeCamp', 'Khan Academy'},
}


def score(course, level, budget, goal=''):
    """Weighted score between 0 and 1:
    0.35 rating + 0.30 level match + 0.15 budget match + 0.10 popularity + 0.10 goal match"""
    rating = float(course['rating']) / 5
    level_fit = 1 - abs(LEVELS[course['level']] - LEVELS[level]) / 2
    budget_fit = 1.0 if course['is_free'] or budget != 'Paid okay' else 0.8
    goal_fit = 1.0 if course['platform'] in GOAL_PLATFORMS.get(goal, ()) else 0.0
    return (0.35 * rating + 0.30 * level_fit + 0.15 * budget_fit
            + 0.10 * course['popularity'] / 100 + 0.10 * goal_fit)


def rank_courses(courses, level, budget, goal='', top=3):
    """Best `top` courses for the learner.
    'Free only' removes paid courses; courses two levels above the learner
    (Advanced for a Beginner) are removed unless that would leave nothing."""
    pool = [c for c in courses if c['is_free']] if budget == 'Free only' else list(courses)
    reachable = [c for c in pool if LEVELS[c['level']] - LEVELS[level] < 2]
    pool = reachable or pool
    return sorted(pool, key=lambda c: score(c, level, budget, goal), reverse=True)[:top]


def assign_weeks(topics, hours_per_week):
    """Topic -> week number it starts in, based on cumulative study hours."""
    hours_per_week = max(1, hours_per_week)
    weeks, used = {}, 0
    for t in topics:
        weeks[t['topic_id']] = used // hours_per_week + 1
        used += t['est_hours']
    return weeks


def grade_quiz(questions, answers):
    """Grade one quiz.
    questions: rows with quiz_id and correct_option; answers: {quiz_id: 'a'..'d'}.
    Returns the percent score, counts, whether it passed, and a per-question review."""
    review, correct = [], 0
    for q in questions:
        chosen = (answers.get(q['quiz_id']) or '').lower()
        right = chosen == q['correct_option'].lower()
        correct += right
        review.append({'quiz_id': q['quiz_id'], 'chosen': chosen,
                       'correct_option': q['correct_option'].lower(), 'right': right})
    total = len(questions)
    percent = round(correct * 100 / total) if total else 0
    return {'percent': percent, 'correct': correct, 'total': total,
            'passed': total > 0 and percent >= PASS_MARK, 'review': review}


def plan_progress(passed_topics, quiz_topics):
    """Roadmap progress is counted in topics, not courses: the courses for a topic
    are alternatives, so finishing the topic's quiz is what completes it."""
    pct = round(passed_topics * 100 / quiz_topics) if quiz_topics else 0
    return {'passed': passed_topics, 'total': quiz_topics, 'percent': pct,
            'complete': quiz_topics > 0 and passed_topics >= quiz_topics}
