"""Starter coding problems for the practice platform.

Each problem is plain data. Expected outputs are never typed in: load_problems() runs the
reference `solution` on every test input, so the stored answers always agree with it.

To add a problem, append a dict to PROBLEMS and run `python seed.py` again. Only new slugs
are inserted, so it is safe to run as often as you like."""
import json
import random
import subprocess
import sys
from collections import Counter

from curriculum import UNIT_NAMES


# ---------------------------------------------------------------- test generators

def _count_pairs(nums, target):
    """How many position pairs i < j add up to target (counted from value frequencies)."""
    freq, pairs = Counter(nums), 0
    for v, c in freq.items():
        w = target - v
        if v < w:
            pairs += c * freq.get(w, 0)
        elif v == w:
            pairs += c * (c - 1) // 2
    return pairs


def _two_sum_input(n, target, nums):
    assert _count_pairs(nums, target) == 1, 'two-sum test must have exactly one pair'
    return f'{n} {target}\n' + ' '.join(map(str, nums)) + '\n'


def _two_sum_generated(seed, n):
    """n distinct numbers with exactly one pair adding up to the target.
    Every number except q is below target/2, so no other pair can reach the target."""
    rng = random.Random(seed)
    target = rng.randint(10, 10 ** 9)
    p = rng.randint(target - 10 ** 9, (target - 1) // 2)
    q = target - p
    pool = rng.sample(range(-10 ** 9, (target + 1) // 2), n - 1)
    others = [v for v in pool if v != p][:n - 2]
    nums = others + [p, q]
    rng.shuffle(nums)
    return _two_sum_input(n, target, nums)


def _two_sum_hand(target, nums):
    return _two_sum_input(len(nums), target, nums)


CLOSER = {'(': ')', '[': ']', '{': '}'}


def _random_balanced(seed, length):
    """A random balanced bracket string of an even length."""
    rng = random.Random(seed)
    out, stack = [], []
    for i in range(length):
        remaining = length - i
        if stack and (len(stack) == remaining or rng.random() < 0.5):
            out.append(CLOSER[stack.pop()])
        else:
            opener = rng.choice('([{')
            stack.append(opener)
            out.append(opener)
    return ''.join(out)


_BIG_BALANCED = _random_balanced(7, 100000)
_BIG_BALANCED_2 = _random_balanced(11, 99998)


# ---------------------------------------------------------------- the problems

PROBLEMS = [
    {
        'slug': 'sum-of-digits',
        'title': 'Sum of Digits',
        'difficulty': 'Easy',
        'pattern': 'Loops',
        'est_minutes': 15,
        'levels': ['Beginner', 'Intermediate'],
        'companies': [],
        'placements': {'exam': (1, 1, 1), 'interest': (1, 2, 3)},
        'statement': (
            'Read a non-negative whole number N and print the sum of its decimal digits.\n\n'
            'For example, the digits of 1204 are 1, 2, 0 and 4, so the answer for 1204 is 7.'),
        'input_format': 'One line containing the integer N.',
        'output_format': 'One integer: the sum of the digits of N.',
        'constraints': ['0 <= N <= 10^9'],
        'examples': [
            {'input': '1234\n', 'output': '10\n', 'explanation': '1 + 2 + 3 + 4 = 10'},
            {'input': '0\n', 'output': '0\n', 'explanation': 'The number 0 has a single digit, 0.'},
        ],
        'hints': [
            'How could you look at just the last digit of a number? What happens to the number '
            'if you then remove that digit?',
            'The remainder after dividing by 10 is the last digit. Integer division by 10 drops it.',
            'Keep a running total. While N is greater than zero: add N % 10 to the total, then '
            'replace N with N // 10. Print the total at the end.',
        ],
        'discussion': [
            'Does your loop still print the right answer when N = 0?',
            'Follow-up: could you do it by treating the input as text instead? Which approach '
            'would you prefer for a number with 10,000 digits?',
        ],
        'editorial': (
            'Each pass of the loop takes off the last digit (N % 10) and discards it (N // 10), '
            'so the loop runs once per digit.\n\n'
            'Time: O(d) for a number with d digits. Space: O(1).\n\n'
            'Alternative: read the input as a string and add up the value of each character. '
            'Both approaches are fine at this size.'),
        'solution': (
            'import sys\n\n'
            'n = int(sys.stdin.readline())\n'
            'total = 0\n'
            'while n > 0:\n'
            '    total += n % 10   # the last digit\n'
            '    n //= 10          # drop it\n'
            'print(total)\n'),
        'public_tests': ['1234\n', '0\n', '90817\n'],
        'hidden_tests': ['5\n', '10\n', '100\n', '999999999\n', '1000000000\n',
                         '123456789\n', '1010101\n', '7000007\n'],
    },
    {
        'slug': 'factorial-recursive',
        'title': 'Factorial with Recursion',
        'difficulty': 'Easy',
        'pattern': 'Recursion',
        'est_minutes': 20,
        'levels': ['Beginner', 'Intermediate'],
        'companies': [],
        'placements': {'exam': (4, 1, 1)},
        'statement': (
            'The factorial of a non-negative integer N, written N!, is the product of all whole '
            'numbers from 1 to N. By definition 0! = 1.\n\n'
            'Print N! using a recursive function: N! = N x (N - 1)!, with a base case that stops '
            'the recursion.'),
        'input_format': 'One line containing the integer N.',
        'output_format': 'One integer: N!',
        'constraints': ['0 <= N <= 18',
                        'The answer is below 2^53, so it is exact in every supported language.'],
        'examples': [
            {'input': '5\n', 'output': '120\n', 'explanation': '5! = 5 x 4 x 3 x 2 x 1 = 120'},
            {'input': '0\n', 'output': '1\n', 'explanation': 'By definition 0! = 1.'},
        ],
        'hints': [
            'If you already knew (N - 1)!, how would you get N! from it?',
            'That is a recursive definition. For which input do you know the answer without '
            'any further recursion?',
            'Return 1 when N is 0 (or 1). Otherwise return N multiplied by the factorial of N - 1.',
        ],
        'discussion': [
            'Trace factorial(3) by hand: write down each call and the value it returns once the '
            'deeper calls have finished.',
            'What happens if you forget the base case?',
            'Why would 21! not fit in a signed 64-bit integer in C++ or Java?',
        ],
        'editorial': (
            'N! = N x (N - 1)! together with 0! = 1 gives a recursion with N + 1 calls.\n\n'
            'Time: O(N). Space: O(N) for the call stack.\n\n'
            'A loop does the same work with O(1) extra space. Here the point of the exercise is '
            'to practise the recursive way of thinking.'),
        'solution': (
            'import sys\n\n\n'
            'def factorial(n):\n'
            '    if n <= 1:          # base case: 0! = 1! = 1\n'
            '        return 1\n'
            '    return n * factorial(n - 1)\n\n\n'
            'print(factorial(int(sys.stdin.readline())))\n'),
        'public_tests': ['5\n', '0\n', '10\n'],
        'hidden_tests': ['1\n', '2\n', '3\n', '7\n', '12\n', '15\n', '17\n', '18\n'],
    },
    {
        'slug': 'two-sum',
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'pattern': 'Hash Map',
        'est_minutes': 25,
        'levels': ['Beginner', 'Intermediate', 'Advanced'],
        'companies': ['Amazon', 'Google', 'Microsoft'],
        'placements': {'interview': (1, 1, 1)},
        'statement': (
            'You are given a list of N integers and a target number T. Exactly one pair of '
            'different positions i < j has a[i] + a[j] equal to T. Print that pair of positions.\n\n'
            'Positions are counted from 0.'),
        'input_format': ('The first line has two integers N and T. '
                         'The second line has N integers a[0] ... a[N-1].'),
        'output_format': 'Two integers i and j with i < j, separated by a space.',
        'constraints': ['2 <= N <= 100000',
                        '-10^9 <= a[i], T <= 10^9',
                        'Exactly one pair of positions adds up to T.',
                        'A sum can reach 2 x 10^9, which does not fit in a signed 32-bit integer.'],
        'examples': [
            {'input': '4 9\n2 7 11 15\n', 'output': '0 1\n', 'explanation': 'a[0] + a[1] = 2 + 7 = 9'},
            {'input': '3 6\n3 2 4\n', 'output': '1 2\n', 'explanation': 'a[1] + a[2] = 2 + 4 = 6'},
            {'input': '2 6\n3 3\n', 'output': '0 1\n',
             'explanation': 'The same value may appear twice, at different positions.'},
        ],
        'hints': [
            'For a number x, which other number would complete the pair? Can you write it as one '
            'expression?',
            'The whole problem is answering "have I seen T - x before?" quickly. Which data '
            'structure answers membership questions in constant time?',
            'Walk through the list once, keeping a dictionary from value to position. For each '
            'position j, check whether T - a[j] is already in the dictionary; if so print its '
            'stored position and j. Otherwise store a[j].',
        ],
        'discussion': [
            'A double loop checks every pair. For N = 100000 how many pairs is that, and roughly '
            'how long would it take?',
            'Why is it safe to remember only one position per value here?',
            'Follow-up: what if the list were sorted? Can you avoid the dictionary?',
        ],
        'editorial': (
            'Brute force checks every pair: O(N^2) time, about 5 billion pairs when N = 100000. '
            'That is far too slow.\n\n'
            'A hash map solves it in one pass. For each element, look up the value that would '
            'complete the pair (T - a[j]) among the elements already seen, then record the '
            'current element.\n\n'
            'Time: O(N). Space: O(N).'),
        'solution': (
            'import sys\n\n\n'
            'def main():\n'
            '    data = sys.stdin.read().split()\n'
            '    n, target = int(data[0]), int(data[1])\n'
            '    nums = list(map(int, data[2:2 + n]))\n'
            '    seen = {}                       # value -> position where we saw it\n'
            '    for j, x in enumerate(nums):\n'
            '        if target - x in seen:      # the partner appeared earlier\n'
            '            print(seen[target - x], j)\n'
            '            return\n'
            '        seen[x] = j\n\n\n'
            'main()\n'),
        'public_tests': ['4 9\n2 7 11 15\n', '3 6\n3 2 4\n', '2 6\n3 3\n'],
        'hidden_tests': [
            _two_sum_hand(0, [-5, 5]),
            _two_sum_hand(-10, [-3, -7, 5, 1]),
            _two_sum_hand(0, [0, 0, 1]),
            _two_sum_hand(8, [5, 1, 6, 2]),
            _two_sum_hand(-3, [-1, -2, 7, 9, 0]),
            _two_sum_generated(1, 10),
            _two_sum_generated(2, 200),
            _two_sum_generated(3, 5000),
            _two_sum_generated(4, 100000),   # a double loop is far too slow here
        ],
    },
    {
        'slug': 'valid-parentheses',
        'title': 'Balanced Brackets',
        'difficulty': 'Easy',
        'pattern': 'Stack',
        'est_minutes': 20,
        'levels': ['Beginner', 'Intermediate'],
        'companies': [],
        'placements': {'interview': (2, 1, 1), 'exam': (5, 2, 10)},
        'statement': (
            'A string is made only of the characters `(`, `)`, `[`, `]`, `{` and `}`. It is '
            'balanced when every opening bracket is closed by the same kind of bracket, and the '
            'brackets are closed in the right order: the most recently opened bracket must be '
            'closed first.\n\n'
            'Print YES if the string is balanced and NO otherwise.'),
        'input_format': 'One line containing the string S.',
        'output_format': 'YES or NO.',
        'constraints': ['1 <= |S| <= 100000', 'S contains only the six bracket characters.'],
        'examples': [
            {'input': '()[]{}\n', 'output': 'YES\n', 'explanation': 'Each pair closes right after it opens.'},
            {'input': '([)]\n', 'output': 'NO\n',
             'explanation': 'The `]` arrives while the most recent open bracket is `(`.'},
            {'input': '{[()]}\n', 'output': 'YES\n', 'explanation': 'The pairs are properly nested.'},
        ],
        'hints': [
            'When a closing bracket arrives, which opening bracket must it match: the first one '
            'you saw, or the latest one that is still unmatched?',
            'Always matching the latest unmatched opener is last-in, first-out behaviour. Which '
            'data structure gives you that?',
            'Push every opening bracket onto a stack. For a closing bracket, the stack must be '
            'non-empty and its top must be the matching opener, which you then pop. At the end '
            'the stack must be empty.',
        ],
        'discussion': [
            'There are two ways a string can fail. One is a wrong closer. What is the other, and '
            'where does your code catch it?',
            'Check these by hand: `(`, `)`, `(()`, `())`.',
            'Follow-up: how would you also report the position of the first mistake?',
        ],
        'editorial': (
            'Scan left to right with a stack of unmatched opening brackets. A closing bracket '
            'must match the top of the stack. Openers left on the stack at the end also make the '
            'string invalid.\n\n'
            'Each character is pushed and popped at most once. Time: O(N). Space: O(N).'),
        'solution': (
            'import sys\n\n'
            's = sys.stdin.readline().strip()\n'
            "match = {')': '(', ']': '[', '}': '{'}\n"
            'stack = []\n'
            'balanced = True\n'
            'for ch in s:\n'
            "    if ch in '([{':\n"
            '        stack.append(ch)\n'
            '    elif not stack or stack.pop() != match[ch]:   # wrong or missing opener\n'
            '        balanced = False\n'
            '        break\n'
            "print('YES' if balanced and not stack else 'NO')\n"),
        'public_tests': ['()[]{}\n', '([)]\n', '{[()]}\n'],
        'hidden_tests': [
            '(\n', ')\n', '()\n', '(()\n', '())\n', '{[(])}\n', '][\n',
            '((()))[[[]]]{{}}\n',
            _BIG_BALANCED + '\n',
            _BIG_BALANCED_2 + '\n',
            '(' * 100000 + '\n',
            _BIG_BALANCED[:-1] + '(\n',      # balanced except for the very last character
        ],
    },
    {
        'slug': 'fizzbuzz',
        'title': 'Fizz and Buzz',
        'difficulty': 'Easy',
        'pattern': 'Loops & Conditions',
        'est_minutes': 10,
        'levels': ['Beginner'],
        'companies': [],
        'placements': {'interest': (1, 1, 1)},
        'statement': (
            'Print the numbers from 1 to N, one per line, with these exceptions: print `Fizz` '
            'instead of the number when it is divisible by 3, `Buzz` when it is divisible by 5, '
            'and `FizzBuzz` when it is divisible by both.'),
        'input_format': 'One line containing the integer N.',
        'output_format': 'N lines, as described above.',
        'constraints': ['1 <= N <= 1000'],
        'examples': [
            {'input': '5\n', 'output': '1\n2\nFizz\n4\nBuzz\n', 'explanation': '3 is Fizz and 5 is Buzz.'},
            {'input': '3\n', 'output': '1\n2\nFizz\n', 'explanation': 'Only 3 is divisible by 3 or 5.'},
        ],
        'hints': [
            'How can you test whether one number divides another exactly?',
            'The remainder operator (%) gives 0 when the division is exact. Does the order in '
            'which you check the cases matter?',
            'Check "divisible by both 3 and 5" first. Then check 3, then 5, and print the number '
            'itself otherwise.',
        ],
        'discussion': [
            'What goes wrong if you test divisibility by 3 before testing both?',
            'Follow-up: can you build each line from two optional pieces, Fizz and Buzz, without '
            'a separate FizzBuzz branch?',
        ],
        'editorial': (
            'One pass from 1 to N with remainder checks. Test the "both" case first, or build '
            'the word from two optional parts.\n\n'
            'Time: O(N). Space: O(1).'),
        'solution': (
            'n = int(input())\n'
            'for i in range(1, n + 1):\n'
            '    if i % 15 == 0:      # divisible by both 3 and 5\n'
            "        print('FizzBuzz')\n"
            '    elif i % 3 == 0:\n'
            "        print('Fizz')\n"
            '    elif i % 5 == 0:\n'
            "        print('Buzz')\n"
            '    else:\n'
            '        print(i)\n'),
        'public_tests': ['5\n', '3\n', '15\n'],
        'hidden_tests': ['1\n', '2\n', '4\n', '10\n', '16\n', '30\n', '100\n', '1000\n'],
    },
]


# ---------------------------------------------------------------- loading into the database

def expected_output(solution, test_input):
    """Run the reference solution on one input and return what it prints."""
    done = subprocess.run([sys.executable, '-I', '-c', solution], input=test_input,
                          capture_output=True, text=True, timeout=30)
    if done.returncode != 0:
        raise RuntimeError('A reference solution crashed:\n' + done.stderr)
    return done.stdout


def load_problems(cur):
    """Insert every problem whose slug is not in the database yet. Returns how many were added."""
    added = 0
    for p in PROBLEMS:
        cur.execute('SELECT problem_id FROM problems WHERE slug=%s', (p['slug'],))
        if cur.fetchall():
            continue
        cur.execute(
            'INSERT INTO problems (slug, title, difficulty, pattern, est_minutes, levels, companies, '
            'statement, input_format, output_format, constraints_text, examples_json, hints_json, '
            'discussion_json, editorial, solution_code, time_limit_ms, memory_limit_mb) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (p['slug'], p['title'], p['difficulty'], p['pattern'], p['est_minutes'],
             ','.join(p['levels']), ', '.join(p['companies']), p['statement'],
             p['input_format'], p['output_format'], '\n'.join(p['constraints']),
             json.dumps(p['examples']), json.dumps(p['hints']), json.dumps(p['discussion']),
             p['editorial'], p['solution'], p.get('time_limit_ms', 2000),
             p.get('memory_limit_mb', 256)))
        pid = cur.lastrowid
        for track, (unit, priority, seq) in p['placements'].items():
            cur.execute('INSERT INTO problem_tracks (problem_id, track, unit_no, unit_name, priority, seq) '
                        'VALUES (%s,%s,%s,%s,%s,%s)',
                        (pid, track, unit, UNIT_NAMES[track][unit], priority, seq))
        tests = [(t, True) for t in p['public_tests']] + [(t, False) for t in p['hidden_tests']]
        for ordinal, (text, is_public) in enumerate(tests, 1):
            cur.execute('INSERT INTO test_cases (problem_id, ordinal, is_public, input_text, expected_text) '
                        'VALUES (%s,%s,%s,%s,%s)',
                        (pid, ordinal, is_public, text, expected_output(p['solution'], text)))
        added += 1
    return added