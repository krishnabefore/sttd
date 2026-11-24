"""Tests for the pure logic in recommender.py. No database needed.
Run from the project folder:  python -m unittest discover -s tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommender import (PASS_MARK, assign_weeks, grade_quiz, plan_progress,
                         rank_courses, score)


def course(title, level='Beginner', rating=4.5, free=True, platform='YouTube', pop=80):
    return {'title': title, 'level': level, 'rating': rating, 'is_free': free,
            'platform': platform, 'popularity': pop}


class ScoreAndRank(unittest.TestCase):
    def test_level_match_beats_mismatch(self):
        match = course('match', level='Beginner')
        far = course('far', level='Advanced')
        self.assertGreater(score(match, 'Beginner', 'No preference'),
                           score(far, 'Beginner', 'No preference'))

    def test_goal_nudges_matching_platform(self):
        udemy = course('hands-on', platform='Udemy')
        edx = course('syllabus', platform='edX')
        self.assertGreater(score(udemy, 'Beginner', 'No preference', 'Job skill'),
                           score(edx, 'Beginner', 'No preference', 'Job skill'))
        self.assertGreater(score(edx, 'Beginner', 'No preference', 'Exam prep'),
                           score(udemy, 'Beginner', 'No preference', 'Exam prep'))

    def test_free_only_removes_paid(self):
        cs = [course('free'), course('paid', free=False)]
        self.assertEqual([c['title'] for c in rank_courses(cs, 'Beginner', 'Free only')], ['free'])

    def test_beginner_does_not_get_advanced(self):
        cs = [course('easy'), course('mid', level='Intermediate'), course('hard', level='Advanced')]
        titles = [c['title'] for c in rank_courses(cs, 'Beginner', 'No preference')]
        self.assertNotIn('hard', titles)

    def test_falls_back_when_only_advanced_exists(self):
        cs = [course('hard', level='Advanced')]
        self.assertEqual(len(rank_courses(cs, 'Beginner', 'No preference')), 1)

    def test_top_limit(self):
        cs = [course(str(i)) for i in range(6)]
        self.assertEqual(len(rank_courses(cs, 'Beginner', 'No preference', top=3)), 3)


class Weeks(unittest.TestCase):
    def test_weeks_follow_cumulative_hours(self):
        topics = [{'topic_id': 1, 'est_hours': 10}, {'topic_id': 2, 'est_hours': 10},
                  {'topic_id': 3, 'est_hours': 5}]
        self.assertEqual(assign_weeks(topics, 10), {1: 1, 2: 2, 3: 3})
        self.assertEqual(assign_weeks(topics, 20), {1: 1, 2: 1, 3: 2})

    def test_zero_hours_does_not_crash(self):
        self.assertEqual(assign_weeks([{'topic_id': 1, 'est_hours': 4}], 0), {1: 1})


QUESTIONS = [{'quiz_id': 1, 'correct_option': 'a'},
             {'quiz_id': 2, 'correct_option': 'b'},
             {'quiz_id': 3, 'correct_option': 'c'}]


class Quiz(unittest.TestCase):
    def test_all_correct_passes(self):
        r = grade_quiz(QUESTIONS, {1: 'a', 2: 'b', 3: 'c'})
        self.assertEqual((r['percent'], r['correct'], r['passed']), (100, 3, True))

    def test_two_of_three_is_67_and_fails(self):
        r = grade_quiz(QUESTIONS, {1: 'a', 2: 'b', 3: 'd'})
        self.assertEqual(r['percent'], 67)
        self.assertLess(r['percent'], PASS_MARK)
        self.assertFalse(r['passed'])

    def test_unanswered_counts_wrong(self):
        r = grade_quiz(QUESTIONS, {1: 'a'})
        self.assertEqual(r['correct'], 1)

    def test_answer_case_is_ignored(self):
        self.assertTrue(grade_quiz(QUESTIONS, {1: 'A', 2: 'B', 3: 'C'})['passed'])

    def test_empty_quiz_never_passes(self):
        self.assertFalse(grade_quiz([], {})['passed'])

    def test_review_marks_each_question(self):
        r = grade_quiz(QUESTIONS, {1: 'a', 2: 'd', 3: 'c'})
        self.assertEqual([x['right'] for x in r['review']], [True, False, True])


class Progress(unittest.TestCase):
    def test_counts_topics_not_courses(self):
        self.assertEqual(plan_progress(1, 3)['percent'], 33)

    def test_complete_when_all_topics_passed(self):
        self.assertTrue(plan_progress(3, 3)['complete'])
        self.assertFalse(plan_progress(2, 3)['complete'])

    def test_no_quiz_topics_is_not_complete(self):
        p = plan_progress(0, 0)
        self.assertEqual(p['percent'], 0)
        self.assertFalse(p['complete'])


if __name__ == '__main__':
    unittest.main()
