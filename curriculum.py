"""Static options shared by the onboarding wizard, the roadmap engine and the seed script."""

ROLES = ['School Student (Class 11-12)', 'College Student', 'Working Professional']

LEVELS = ['Absolute Beginner', 'Intermediate', 'Advanced']

# What the learner picks -> the track of problems we build the roadmap from.
GOALS = {
    'Academic / Exams': 'exam',
    'Technical Interviews': 'interview',
    'Personal Interest': 'interest',
}

TRACKS = {
    'exam': {
        'title': 'Exam track',
        'blurb': 'Syntax fundamentals, strings, arrays, recursion and dry-run tracing, '
                 'with syllabus-style questions.',
    },
    'interview': {
        'title': 'Interview track',
        'blurb': 'DSA patterns (two pointers, sliding window, binary search, DP, graphs) '
                 'with a focus on time and space complexity.',
    },
    'interest': {
        'title': 'Skill-building track',
        'blurb': 'Real-world mini-challenges, clean code and getting fluent in your language.',
    },
}

UNIT_NAMES = {
    'exam': {1: 'Programming Basics', 2: 'Strings', 3: 'Arrays & 2D Arrays',
             4: 'Recursion & Dry-Run Tracing', 5: 'Searching, Sorting & Stacks'},
    'interview': {1: 'Arrays & Hashing', 2: 'Two Pointers & Stacks', 3: 'Sliding Window',
                  4: 'Binary Search', 5: 'Dynamic Programming', 6: 'Graphs (BFS/DFS)'},
    'interest': {1: 'Warm-up Challenges', 2: 'Text & Data Tinkering', 3: 'Real-World Mini Projects'},
}

TIMELINES = [(30, '30 days'), (90, '3 months'), (180, '6 months')]
MIN_DEADLINE_DAYS, MAX_DEADLINE_DAYS = 7, 365

DAILY_MINUTES = [(30, '30 min'), (60, '1 hour'), (90, '1.5 hours'), (120, '2 hours')]
MIN_DAILY_MINUTES, MAX_DAILY_MINUTES = 15, 480

LANGUAGES = ['Python', 'C++', 'Java', 'JavaScript']

PRIORITY_LABELS = {1: 'Core', 2: 'Important', 3: 'Stretch'}