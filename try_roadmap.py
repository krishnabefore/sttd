"""Quick check: build a roadmap from the problems in the database and print it.
Run from the project folder:  python try_roadmap.py"""
from db import query
from roadmap import build_roadmap

for track in ('exam', 'interview', 'interest'):
    rows = query('SELECT p.problem_id, p.slug, p.est_minutes, p.levels, t.priority '
                 'FROM problem_tracks t JOIN problems p ON p.problem_id = t.problem_id '
                 'WHERE t.track=%s ORDER BY t.unit_no, t.seq', (track,))
    candidates = [dict(r, levels=set(r['levels'].split(','))) for r in rows]
    plan = build_roadmap(candidates, 'Intermediate', 30, 60)
    slugs = {r['problem_id']: r['slug'] for r in rows}
    print(f'\n{track} track (30 days, 60 min/day):')
    for pid, day in sorted(plan['assignment'].items(), key=lambda item: item[1]):
        print(f'  day {day}: {slugs[pid]}')