"""Creates the database + tables (schema.sql) and loads sample data:
subjects, topics, courses, practice questions and quiz questions.
Run once:  python seed.py"""
import os
from urllib.parse import quote
from db import DB

# Every course links to that platform's search page for its title, so links never break.
SEARCH = {
    'YouTube': 'https://www.youtube.com/results?search_query=',
    'Coursera': 'https://www.coursera.org/search?query=',
    'Udemy': 'https://www.udemy.com/courses/search/?q=',
    'edX': 'https://www.edx.org/search?q=',
    'freeCodeCamp': 'https://www.freecodecamp.org/news/search/?query=',
    'Khan Academy': 'https://www.khanacademy.org/search?page_search_query=',
}

# subject -> [(topic, est_hours, [(title, platform, level, rating, price_label, popularity)])]
# NOTE: ratings, prices and popularity are SAMPLE values. Replace with real ones.
DATA = {
    'Data Structures': [
        ('Arrays & Complexity', 5, [
            ('Big-O Notation Explained', 'YouTube', 'Beginner', 4.8, 'FREE', 90),
            ('Data Structures and Algorithms Specialization', 'Coursera', 'Beginner', 4.7, 'FREE TO AUDIT', 85),
            ('Data Structures Bootcamp', 'Udemy', 'Intermediate', 4.6, '₹499', 70)]),
        ('Linked Lists', 4, [
            ('Linked Lists for Beginners', 'YouTube', 'Beginner', 4.6, 'FREE', 80),
            ('Linked Lists Explained', 'freeCodeCamp', 'Beginner', 4.5, 'FREE', 65),
            ('Master Data Structures in Depth', 'Udemy', 'Advanced', 4.7, '₹549', 60)]),
        ('Trees & Recursion', 6, [
            ('Recursion and Trees Explained', 'YouTube', 'Intermediate', 4.9, 'FREE', 88),
            ('Trees and Traversals', 'Khan Academy', 'Beginner', 4.4, 'FREE', 55),
            ('Applied Algorithms and Trees', 'edX', 'Advanced', 4.8, '$49', 50)]),
    ],
    'Web Development': [
        ('HTML & CSS Basics', 5, [
            ('HTML and CSS Crash Course', 'YouTube', 'Beginner', 4.8, 'FREE', 92),
            ('Responsive Web Design', 'freeCodeCamp', 'Beginner', 4.7, 'FREE', 88),
            ('Complete Web Design Bootcamp', 'Udemy', 'Beginner', 4.6, '₹499', 75)]),
        ('JavaScript Fundamentals', 8, [
            ('JavaScript Full Course for Beginners', 'YouTube', 'Beginner', 4.8, 'FREE', 95),
            ('JavaScript Algorithms and Data Structures', 'freeCodeCamp', 'Intermediate', 4.7, 'FREE', 80),
            ('The Complete JavaScript Course', 'Udemy', 'Intermediate', 4.7, '₹549', 85)]),
        ('Backend with Python & Flask', 6, [
            ('Flask Tutorial for Beginners', 'YouTube', 'Beginner', 4.7, 'FREE', 78),
            ('Python Web Applications with Flask', 'Coursera', 'Intermediate', 4.5, 'FREE TO AUDIT', 60),
            ('REST APIs with Flask', 'Udemy', 'Advanced', 4.6, '₹599', 55)]),
    ],
    'Machine Learning': [
        ('Python for Data Science', 6, [
            ('Python for Data Analysis Basics', 'YouTube', 'Beginner', 4.7, 'FREE', 85),
            ('Scientific Computing with Python', 'freeCodeCamp', 'Beginner', 4.6, 'FREE', 70),
            ('Python for Data Science Bootcamp', 'Udemy', 'Intermediate', 4.6, '₹499', 72)]),
        ('Regression & Classification', 8, [
            ('Machine Learning Specialization', 'Coursera', 'Beginner', 4.9, 'FREE TO AUDIT', 97),
            ('Machine Learning Crash Course', 'YouTube', 'Intermediate', 4.7, 'FREE', 80),
            ('Applied Machine Learning', 'edX', 'Advanced', 4.6, '$49', 58)]),
        ('Neural Networks Introduction', 8, [
            ('Neural Networks From Scratch', 'YouTube', 'Intermediate', 4.9, 'FREE', 90),
            ('Deep Learning Specialization', 'Coursera', 'Intermediate', 4.8, 'FREE TO AUDIT', 92),
            ('Deep Learning A-Z', 'Udemy', 'Advanced', 4.5, '₹549', 65)]),
    ],
}

LC = 'https://leetcode.com/problems/'

# topic name -> [(title, difficulty, url or None)]
# DS problems are real LeetCode problems; the other subjects have no LeetCode
# equivalent, so they get small build-it-yourself tasks (url None).
PRACTICE = {
    'Arrays & Complexity': [
        ('Two Sum', 'Easy', LC + 'two-sum/'),
        ('Best Time to Buy and Sell Stock', 'Easy', LC + 'best-time-to-buy-and-sell-stock/'),
        ('Contains Duplicate', 'Easy', LC + 'contains-duplicate/')],
    'Linked Lists': [
        ('Reverse Linked List', 'Easy', LC + 'reverse-linked-list/'),
        ('Linked List Cycle', 'Easy', LC + 'linked-list-cycle/'),
        ('Merge Two Sorted Lists', 'Easy', LC + 'merge-two-sorted-lists/')],
    'Trees & Recursion': [
        ('Maximum Depth of Binary Tree', 'Easy', LC + 'maximum-depth-of-binary-tree/'),
        ('Invert Binary Tree', 'Easy', LC + 'invert-binary-tree/'),
        ('Validate Binary Search Tree', 'Medium', LC + 'validate-binary-search-tree/')],
    'HTML & CSS Basics': [
        ('Build a responsive navbar with flexbox', 'Easy', None),
        ('Lay out a three-column card grid with CSS grid', 'Medium', None)],
    'JavaScript Fundamentals': [
        ('Write a function that reverses a string', 'Easy', None),
        ('Build a to-do list that adds and removes items', 'Medium', None)],
    'Backend with Python & Flask': [
        ('Create a /hello route that returns JSON', 'Easy', None),
        ('Build a form that saves entries and lists them on a page', 'Medium', None)],
    'Python for Data Science': [
        ('Load a CSV with pandas and print summary statistics', 'Easy', None),
        ('Find and fill the missing values in a dataset', 'Medium', None)],
    'Regression & Classification': [
        ('Fit a linear regression and report its R-squared', 'Medium', None),
        ('Train a classifier and print its accuracy on a test split', 'Medium', None)],
    'Neural Networks Introduction': [
        ('Implement a single neuron with a sigmoid activation', 'Medium', None),
        ('Train a small network to learn XOR', 'Hard', None)],
}

# topic name -> [(prompt, [option a, b, c, d], correct letter)]
QUIZ = {
    'Arrays & Complexity': [
        ('What is the time complexity of reading an array element by its index?',
         ['O(n)', 'O(1)', 'O(log n)', 'O(n log n)'], 'b'),
        ('Binary search on a sorted array of n items takes about how many steps?',
         ['O(n)', 'O(1)', 'O(n^2)', 'O(log n)'], 'd'),
        ('Two nested loops that each run n times give which time complexity?',
         ['O(n^2)', 'O(2n)', 'O(log n)', 'O(n)'], 'a')],
    'Linked Lists': [
        ('Inserting a new node at the head of a singly linked list takes:',
         ['O(n)', 'O(log n)', 'O(1)', 'O(n^2)'], 'c'),
        ('Which technique detects a cycle in a linked list?',
         ['Binary search', "Floyd's tortoise and hare", 'Merge sort', 'Breadth-first search'], 'b'),
        ('Compared with an array, a linked list lacks:',
         ['Dynamic size', 'Cheap insertion at the head', 'Constant-time access by index', 'Pointers'], 'c')],
    'Trees & Recursion': [
        ('An in-order traversal of a binary search tree visits values in:',
         ['Random order', 'Descending order', 'Level order', 'Ascending order'], 'd'),
        ('Every correct recursive function needs:',
         ['A base case', 'A global variable', 'A loop', 'An array'], 'a'),
        ('The maximum number of nodes at level k of a binary tree (root is level 0) is:',
         ['k', '2k', '2^k', 'k^2'], 'c')],
    'HTML & CSS Basics': [
        ('Which HTML tag creates the largest heading?',
         ['<h6>', '<head>', '<heading>', '<h1>'], 'd'),
        ('Which CSS property changes the colour of text?',
         ['color', 'font-style', 'background', 'text-decoration'], 'a'),
        ('From the inside out, the CSS box model is:',
         ['margin, border, padding, content', 'content, padding, border, margin',
          'content, margin, padding, border', 'padding, content, margin, border'], 'b')],
    'JavaScript Fundamentals': [
        ('Which keyword declares a block-scoped variable that can be reassigned?',
         ['var', 'const', 'let', 'static'], 'c'),
        ('What does typeof null return in JavaScript?',
         ['"null"', '"undefined"', '"number"', '"object"'], 'd'),
        ('Which array method adds an element to the end?',
         ['push()', 'pop()', 'shift()', 'unshift()'], 'a')],
    'Backend with Python & Flask': [
        ('Which HTTP method is normally used to submit a form that creates data?',
         ['GET', 'POST', 'HEAD', 'TRACE'], 'b'),
        ('Which Flask decorator maps a URL to a function?',
         ['@app.run', '@app.url', '@app.route', '@app.view'], 'c'),
        ('Which status code means the resource was not found?',
         ['200', '301', '500', '404'], 'd')],
    'Python for Data Science': [
        ('Which library is built around the DataFrame?',
         ['pandas', 'flask', 'requests', 'turtle'], 'a'),
        ("NumPy's core data structure is the:",
         ['dict', 'n-dimensional array (ndarray)', 'linked list', 'set'], 'b'),
        ('By default, df.head() shows:',
         ['The last 5 rows', 'The column names only', 'The first 5 rows', 'A random row'], 'c')],
    'Regression & Classification': [
        ('Predicting a continuous number, such as a house price, is called:',
         ['Clustering', 'Classification', 'Regression', 'Sorting'], 'c'),
        ('Overfitting means the model:',
         ['Is too simple to learn anything',
          'Fits the training data too closely and does poorly on new data',
          'Trains too quickly', 'Has too few features'], 'b'),
        ('Which of these is a classification metric?',
         ['Mean squared error', 'R-squared', 'Mean absolute error', 'Accuracy'], 'd')],
    'Neural Networks Introduction': [
        ('Which component adds non-linearity to a neural network?',
         ['Activation function', 'Loss label', 'Batch index', 'Dataset split'], 'a'),
        ('Gradients for training are computed with:',
         ['Binary search', 'Backpropagation', 'Hashing', 'Normalisation'], 'b'),
        ('The learning rate controls:',
         ['The number of layers', 'The size of the dataset',
          'How big each weight update is', 'The number of classes'], 'c')],
}


def load(cur):
    """Insert all subjects, topics and courses using an open cursor."""
    for subject, topics in DATA.items():
        cur.execute('INSERT INTO subjects (name) VALUES (%s)', (subject,))
        sid = cur.lastrowid
        for order, (tname, hours, courses) in enumerate(topics, 1):
            cur.execute('INSERT INTO topics (subject_id, name, sequence_order, est_hours) '
                        'VALUES (%s,%s,%s,%s)', (sid, tname, order, hours))
            tid = cur.lastrowid
            for title, platform, level, rating, price, pop in courses:
                cur.execute('INSERT INTO courses (topic_id, title, platform, url, level, rating, '
                            'is_free, price_label, popularity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                            (tid, title, platform, SEARCH[platform] + quote(title), level, rating,
                             price.startswith('FREE'), price, pop))
            for qtitle, diff, qurl in PRACTICE.get(tname, []):
                cur.execute('INSERT INTO questions (topic_id, title, difficulty, url) '
                            'VALUES (%s,%s,%s,%s)', (tid, qtitle, diff, qurl))
            for prompt, opts, right in QUIZ.get(tname, []):
                cur.execute('INSERT INTO quiz_questions (topic_id, prompt, option_a, option_b, '
                            'option_c, option_d, correct_option) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                            (tid, prompt, *opts, right))


def main():
    import mysql.connector
    cfg = {k: v for k, v in DB.items() if k != 'database'}
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), encoding='utf-8') as f:
        for stmt in f.read().split(';'):
            if stmt.strip():
                cur.execute(stmt)
    cur.execute('SELECT COUNT(*) FROM subjects')
    if cur.fetchone()[0]:
        print('Database already has data, nothing to do.')
    else:
        load(cur)
        conn.commit()
        print('Database created and sample data loaded.')
    conn.close()


if __name__ == '__main__':
    main()
