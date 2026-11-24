"""Tests for roadmap.py (pure logic, no database).
Run from the project folder:  python -m unittest discover -s tests"""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import roadmap as rm

ALL = {'Beginner', 'Intermediate', 'Advanced'}


def cand(pid, est=30, priority=1, levels=ALL):
    return {'problem_id': pid, 'est_minutes': est, 'priority': priority, 'levels': set(levels)}


def items_from(assignment, cands, status='pending'):
    """Turn a build_roadmap assignment into replan() items."""
    by_id = {c['problem_id']: (i, c) for i, c in enumerate(cands)}
    return [dict(c, order=i, status=status, day_no=assignment.get(pid))
            for pid, (i, c) in by_id.items() if pid in assignment]


class Dates(unittest.TestCase):
    def test_day_index(self):
        self.assertEqual(rm.day_index('2026-11-24', date(2026, 11, 24)), 1)
        self.assertEqual(rm.day_index('2026-11-24', date(2026, 11, 30)), 7)
        self.assertEqual(rm.day_index('2026-11-24', date(2026, 11, 1)), 1)  # never below 1

    def test_review_days_only_in_longer_plans(self):
        self.assertTrue(rm.is_review_day(7, True))
        self.assertFalse(rm.is_review_day(7, False))
        self.assertFalse(rm.is_review_day(6, True))


class Build(unittest.TestCase):
    def test_everything_fits_and_review_days_stay_empty(self):
        cands = [cand(i) for i in range(1, 11)]          # 10 x 30 min
        r = rm.build_roadmap(cands, 'Intermediate', 30, 60)
        self.assertEqual(len(r['assignment']), 10)
        self.assertEqual(r['backlog'], [])
        self.assertTrue(all(not rm.is_review_day(d, True) for d in r['assignment'].values()))
        self.assertEqual(r['final_day'], 5)               # two per day

    def test_curriculum_order_is_kept(self):
        cands = [cand(i) for i in range(1, 9)]
        days = rm.build_roadmap(cands, 'Intermediate', 30, 60)['assignment']
        self.assertEqual([days[i] for i in range(1, 9)], sorted(days.values()))

    def test_least_important_are_dropped_first(self):
        cands = [cand(1, priority=1), cand(2, priority=3), cand(3, priority=1), cand(4, priority=2)]
        # 7-day plan = 7 working days, but only 60 minutes in total is affordable here
        r = rm.build_roadmap(cands, 'Intermediate', 1, 60)  # 1 day x 60 min -> two 30-min problems
        self.assertEqual(set(r['assignment']), {1, 3})
        self.assertEqual(set(r['backlog']), {2, 4})

    def test_problem_longer_than_a_day_gets_its_own_day(self):
        cands = [cand(1, est=100), cand(2, est=20)]
        a = rm.build_roadmap(cands, 'Intermediate', 10, 60)['assignment']
        self.assertEqual(a[1], 1)
        self.assertEqual(a[2], 2)

    def test_level_filter_and_fallback(self):
        cands = [cand(i, levels={'Beginner'}) for i in range(1, 4)] + \
                [cand(i, levels=ALL) for i in range(4, 10)]
        adv = rm.build_roadmap(cands, 'Advanced', 30, 60)
        self.assertEqual(set(adv['assignment']), set(range(4, 10)))
        self.assertEqual(adv['skipped_for_level'], 3)
        few = [cand(1, levels={'Beginner'}), cand(2, levels=ALL)]       # fewer than MIN_POOL fit
        self.assertEqual(set(rm.build_roadmap(few, 'Advanced', 30, 60)['assignment']), {1, 2})

    def test_empty_candidates(self):
        r = rm.build_roadmap([], 'Intermediate', 30, 60)
        self.assertEqual((r['assignment'], r['final_day']), ({}, 0))

    def test_never_schedules_past_the_deadline(self):
        cands = [cand(i, est=45) for i in range(1, 40)]
        r = rm.build_roadmap(cands, 'Intermediate', 14, 60)
        self.assertLessEqual(max(r['assignment'].values()), 14)
        self.assertTrue(r['backlog'])


class Replan(unittest.TestCase):
    def setUp(self):
        self.cands = [cand(i) for i in range(1, 21)]      # 20 x 30 min, 2 per day
        self.built = rm.build_roadmap(self.cands, 'Intermediate', 30, 60)

    def run_replan(self, items, today, **kw):
        return rm.replan(items, today, 30, 60, True, **kw)

    def test_on_track_changes_nothing(self):
        items = items_from(self.built['assignment'], self.cands)
        r = self.run_replan(items, 1)
        self.assertEqual(r['summary']['status'], 'on_track')
        self.assertEqual(r['assignment'], self.built['assignment'])

    def test_missed_days_move_work_forward(self):
        items = items_from(self.built['assignment'], self.cands)
        r = self.run_replan(items, 5)                      # days 1-4 passed, nothing solved
        s = r['summary']
        self.assertEqual(s['status'], 'behind')
        self.assertEqual(s['missed'], 8)
        self.assertEqual(s['backlogged'], 0)
        self.assertTrue(all(d >= 5 for d in r['assignment'].values()))

    def test_far_behind_parks_least_important(self):
        cands = [cand(i, priority=1 if i <= 12 else 3) for i in range(1, 25)]
        built = rm.build_roadmap(cands, 'Intermediate', 14, 60)
        self.assertEqual(built['backlog'], [])
        items = items_from(built['assignment'], cands)
        r = rm.replan(items, 8, 14, 60, True)              # 6 working days left = 12 problems
        parked = [pid for pid, d in r['assignment'].items() if d is None]
        self.assertEqual(len(parked), 12)
        self.assertTrue(all(pid > 12 for pid in parked))   # only the stretch ones
        self.assertEqual(r['summary']['status'], 'behind')

    def test_ahead_pulls_the_plan_forward(self):
        items = items_from(self.built['assignment'], self.cands)
        for it in items[:6]:                               # solved 6 problems on day 1
            it['status'] = 'done'
        r = self.run_replan(items, 1, done_today_minutes=180)
        s = r['summary']
        self.assertEqual(s['status'], 'ahead')
        self.assertGreater(s['days_saved'], 0)
        pending = {pid: d for pid, d in r['assignment'].items() if d}
        self.assertLess(max(pending.values()), self.built['final_day'])

    def test_backlog_comes_back_when_there_is_room(self):
        cands = [cand(i) for i in range(1, 7)]
        items = [dict(c, order=i, status='pending', day_no=1 + i // 2) for i, c in enumerate(cands[:5])]
        items.append(dict(cands[5], order=5, status='backlog', day_no=None))
        r = self.run_replan(items, 1)
        self.assertEqual(r['summary']['restored'], 1)
        self.assertIsNotNone(r['assignment'][6])

    def test_overdue_plan_is_extended_two_weeks(self):
        items = items_from(self.built['assignment'], self.cands)
        r = self.run_replan(items, 35)
        self.assertTrue(r['summary']['overdue'])
        days = [d for d in r['assignment'].values() if d]
        self.assertTrue(days and min(days) >= 35 and max(days) <= 35 + rm.EXTENSION_DAYS)

    def test_work_done_today_uses_up_todays_time(self):
        items = items_from(self.built['assignment'], self.cands)
        items[0]['status'] = 'done'
        r = self.run_replan(items, 1, done_today_minutes=60)   # a full day already studied
        self.assertTrue(all(d >= 2 for d in r['assignment'].values() if d))

    def test_done_items_are_left_alone(self):
        items = items_from(self.built['assignment'], self.cands)
        items[0]['status'] = 'done'
        r = self.run_replan(items, 1)
        self.assertNotIn(items[0]['problem_id'], r['assignment'])

    def test_note_is_always_a_sentence(self):
        items = items_from(self.built['assignment'], self.cands)
        for today in (1, 5, 35):
            note = self.run_replan(items, today)['summary']['note']
            self.assertTrue(note.endswith('.'))


class Views(unittest.TestCase):
    def test_group_by_week(self):
        entries = [{'day_no': 1}, {'day_no': 9}, {'day_no': None}]
        weeks, last = rm.group_by_week(entries, True)
        self.assertEqual((len(weeks), last), (2, 9))
        self.assertTrue(weeks[0]['days'][6]['review'])     # day 7
        self.assertEqual(len(weeks[1]['days'][1]['entries']), 1)   # day 9

    def test_group_by_week_with_nothing_scheduled(self):
        weeks, last = rm.group_by_week([], False)
        self.assertEqual((len(weeks), last), (1, 1))

    def test_streak(self):
        today = date(2026, 11, 24)
        days = [date(2026, 11, 24), date(2026, 11, 23), date(2026, 11, 22), date(2026, 11, 20)]
        self.assertEqual(rm.streak(days, today), 3)
        self.assertEqual(rm.streak(days[1:], today), 2)        # nothing yet today: counts back from yesterday
        self.assertEqual(rm.streak([], today), 0)
        self.assertEqual(rm.streak(['2026-11-23'], today), 1)  # ISO strings work too


if __name__ == '__main__':
    unittest.main()