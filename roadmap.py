"""The roadmap engine: chooses problems for a learner, packs them into days, and
re-plans when the learner falls behind or races ahead.

Pure Python (no database, no Flask), so it is easy to test.

A candidate / item is a dict with:
    problem_id, est_minutes, priority (1 core, 2 important, 3 stretch),
    levels (set of 'Beginner' / 'Intermediate' / 'Advanced')
Re-planning items also carry: order (curriculum position), status, day_no."""
import math
from datetime import date, datetime, timedelta

LEVEL_KEYS = {'Absolute Beginner': 'Beginner', 'Beginner': 'Beginner',
              'Intermediate': 'Intermediate', 'Advanced': 'Advanced'}

REVIEW_EVERY = 7          # every 7th day is a light review / catch-up day ...
MIN_REVIEW_PLAN_DAYS = 14  # ... in plans of at least this many days
MIN_POOL = 5              # if fewer problems suit the level, ignore the level filter
EXTENSION_DAYS = 14       # how far a plan is stretched once its deadline has passed


# ---------------------------------------------------------------- dates and days

def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def day_index(start_date, today):
    """Day 1 is the start date. Never less than 1."""
    return max(1, (to_date(today) - to_date(start_date)).days + 1)


def level_key(level):
    return LEVEL_KEYS.get(level, 'Beginner')


def is_review_day(day, has_review):
    return has_review and day % REVIEW_EVERY == 0


def working_days(first_day, last_day, has_review):
    return [d for d in range(first_day, last_day + 1) if not is_review_day(d, has_review)]


# ---------------------------------------------------------------- choosing and packing

def select_items(candidates, capacity):
    """Take core problems first, then important, then stretch (curriculum order inside each
    group), each only while it still fits in `capacity` minutes.
    Returns (chosen in curriculum order, left out in curriculum order)."""
    chosen_ids, used = set(), 0
    for priority in (1, 2, 3):
        for c in candidates:
            if c['priority'] == priority and used + c['est_minutes'] <= capacity:
                chosen_ids.add(c['problem_id'])
                used += c['est_minutes']
    chosen = [c for c in candidates if c['problem_id'] in chosen_ids]
    left_out = [c for c in candidates if c['problem_id'] not in chosen_ids]
    return chosen, left_out


def pack_days(items, first_day, last_day, minutes_per_day, has_review, used_first_day=0):
    """Place items, in order, onto days without splitting a problem across days.
    A problem longer than a whole day gets a day to itself.
    Returns ({problem_id: day_no}, items that did not fit before last_day)."""
    assignment, overflow = {}, []
    day, left = first_day, minutes_per_day - used_first_day
    for item in items:
        est = max(1, int(item['est_minutes']))
        while day <= last_day:
            if is_review_day(day, has_review):
                day, left = day + 1, minutes_per_day
                continue
            if est <= left or left == minutes_per_day:
                assignment[item['problem_id']] = day
                left -= est
                break
            day, left = day + 1, minutes_per_day
        else:
            overflow.append(item)
    return assignment, overflow


def fit_schedule(candidates, first_day, last_day, minutes_per_day, has_review, used_first_day=0):
    """Choose what fits between first_day and last_day, then pack it.
    Returns (assignment, chosen, left_out). Least important problems are dropped first."""
    days = working_days(first_day, last_day, has_review)
    capacity = len(days) * minutes_per_day
    if days and days[0] == first_day:
        capacity -= used_first_day
    chosen, left_out = select_items(candidates, max(0, capacity))
    while True:
        assignment, overflow = pack_days(chosen, first_day, last_day, minutes_per_day,
                                         has_review, used_first_day)
        if not overflow:
            break
        # Bin-packing can overflow even when the minutes add up: drop the least important item.
        victim = max(chosen, key=lambda c: (c['priority'], c['order']))
        chosen = [c for c in chosen if c is not victim]
        left_out.append(victim)
    left_out.sort(key=lambda c: c['order'])
    return assignment, chosen, left_out


# ---------------------------------------------------------------- building a roadmap

def build_roadmap(candidates, level, total_days, minutes_per_day):
    """candidates: the track's problems in curriculum order.
    Returns {'assignment': {problem_id: day}, 'backlog': [problem_id], 'final_day': int,
             'has_review': bool, 'skipped_for_level': int}"""
    lvl = level_key(level)
    ordered = [dict(c, order=i) for i, c in enumerate(candidates)]
    pool = [c for c in ordered if lvl in c['levels']]
    if len(pool) < MIN_POOL:
        pool = ordered
    has_review = total_days >= MIN_REVIEW_PLAN_DAYS
    assignment, chosen, left_out = fit_schedule(pool, 1, total_days, minutes_per_day, has_review)
    return {
        'assignment': assignment,
        'backlog': [c['problem_id'] for c in left_out],
        'final_day': max(assignment.values()) if assignment else 0,
        'has_review': has_review,
        'skipped_for_level': len(ordered) - len(pool),
    }


# ---------------------------------------------------------------- adaptive re-planning

def replan(items, today, total_days, minutes_per_day, has_review, done_today_minutes=0):
    """Re-plan everything that is not solved yet, starting from day `today`.

    items: dicts with problem_id, est_minutes, priority, order, status
           ('pending' | 'backlog' | 'done') and day_no (None for backlog).
    Returns {'assignment': {problem_id: day_no or None}, 'summary': {...}}.
    Behind schedule: missed work moves forward and, if the deadline is at risk, the least
    important problems are parked in the backlog. Ahead of schedule: the rest moves up and
    parked problems come back if there is room."""
    todo = sorted((i for i in items if i['status'] in ('pending', 'backlog')),
                  key=lambda i: i['order'])
    old_days = [i['day_no'] for i in items if i['status'] == 'pending' and i['day_no']]
    old_final = max(old_days) if old_days else 0

    overdue = today > total_days
    last_day = today + EXTENSION_DAYS if overdue else total_days
    missed = [i for i in todo if i['status'] == 'pending' and i['day_no'] and i['day_no'] < today]
    done_early = [i for i in items if i['status'] == 'done' and i['day_no'] and i['day_no'] > today]
    used_today = 0 if is_review_day(today, has_review) else max(0, done_today_minutes)

    assignment, chosen, left_out = fit_schedule(todo, today, last_day, minutes_per_day,
                                                has_review, used_today)
    result = {i['problem_id']: assignment.get(i['problem_id']) for i in todo}

    moved = sum(1 for i in chosen if i['status'] == 'pending' and i['day_no']
                and i['day_no'] != assignment[i['problem_id']])
    backlogged = [i for i in left_out if i['status'] == 'pending']
    restored = [i for i in chosen if i['status'] == 'backlog']
    new_final = max(assignment.values()) if assignment else 0
    days_saved = max(0, old_final - new_final) if old_final and new_final else 0

    if missed or backlogged or overdue:
        status = 'behind'
    elif done_early or restored or days_saved:
        status = 'ahead'
    else:
        status = 'on_track'

    summary = {'status': status, 'moved': moved, 'backlogged': len(backlogged),
               'restored': len(restored), 'days_saved': days_saved, 'final_day': new_final,
               'overdue': overdue, 'missed': len(missed)}
    summary['note'] = _note(summary)
    return {'assignment': result, 'summary': summary}


def _plural(n, word):
    return f'{n} {word}{"" if n == 1 else "s"}'


def _note(s):
    if s['status'] == 'on_track':
        return "You're on track. No changes were needed."
    if s['status'] == 'ahead':
        parts = ["You're ahead of schedule, so the rest of your plan moved up"]
        if s['days_saved']:
            parts[0] += f' by {_plural(s["days_saved"], "day")}'
        if s['restored']:
            parts.append(f'{_plural(s["restored"], "parked problem")} came back into the plan')
        return '. '.join(parts) + '.'
    parts = []
    if s['overdue']:
        parts.append('Your deadline has passed, so the plan was extended by two weeks')
    if s['missed']:
        parts.append(f'{_plural(s["missed"], "missed problem")} moved to today or later')
    if s['backlogged']:
        parts.append(f'{_plural(s["backlogged"], "lower-priority problem")} parked in the backlog '
                     f'to protect your deadline')
    if not parts:
        parts.append('The schedule was adjusted to your progress')
    return '. '.join(parts) + '.'


# ---------------------------------------------------------------- views and stats

def group_by_week(entries, has_review):
    """entries: dicts with day_no. Returns (weeks, last_scheduled_day).
    weeks = [{'week': n, 'days': [{'day': d, 'review': bool, 'entries': [...]}, ...]}]"""
    scheduled = [e for e in entries if e.get('day_no')]
    last = max((e['day_no'] for e in scheduled), default=1)
    weeks = []
    for w in range(1, math.ceil(last / 7) + 1):
        days = []
        for d in range((w - 1) * 7 + 1, w * 7 + 1):
            days.append({'day': d, 'review': is_review_day(d, has_review),
                         'entries': [e for e in scheduled if e['day_no'] == d]})
        weeks.append({'week': w, 'days': days})
    return weeks, last


def streak(solve_dates, today):
    """Consecutive days (ending today, or yesterday if nothing solved yet today) with a solve."""
    solved = {to_date(d) for d in solve_dates}
    day = to_date(today)
    if day not in solved:
        day -= timedelta(days=1)
    n = 0
    while day in solved:
        n += 1
        day -= timedelta(days=1)
    return n