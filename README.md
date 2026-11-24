# StudyPath (merged with CogniPath's quizzes and practice)

Tell the app who you are and what you want to learn. It builds a week-by-week
roadmap, and each topic comes with ranked courses, practice questions and a short
quiz. Pass the quiz (70% or more) to complete the topic; pass every topic to
complete the course.

## Run it

1. Install Python (tick "Add Python to PATH") and MySQL Community Server.
2. Double-click `setup.bat` once. It installs the libraries, asks for your
   MySQL root password (not saved), creates the project's MySQL login and
   loads the sample data.
3. Double-click `start.bat` any time to run the app. It opens in your browser.



## How it is organised

| Part | Files | Job |
|---|---|---|
| Frontend | `templates/`, `static/` | 5-step wizard, dashboard, quiz page |
| Backend | `app.py`, `recommender.py` | Routes; ranking, week planning, quiz grading |
| Database | `schema.sql`, `db.py`, `seed.py` | Tables, connection helper, sample data |

## What a student does

1. **About you:** name and course (High School, 11th, 12th, BTech, BCA, Other).
2. **Subject, level, goal, budget, hours per week.** These shape the roadmap:
   level and budget filter and rank courses, the goal nudges which platforms rank
   higher, and hours per week sets the week each topic starts.
3. **Dashboard:** for each topic, learn (ranked courses, tick when watched),
   practise (LeetCode problems or small tasks), then take the quiz.
4. **Progress counts topics, not courses.** A topic is complete when its quiz is
   passed. The best score is kept, and a later failed retake never undoes a pass.

## Routes

| Route | Purpose |
|---|---|
| `GET /` | Wizard |
| `POST /build-plan` | Save learner and plan, then redirect to the dashboard |
| `GET /plan/<id>` | Dashboard |
| `GET, POST /plan/<id>/quiz/<topic_id>` | Show a quiz, grade it, save progress |
| `POST /api/items/<id>/toggle` | Tick or untick a course as watched |

## Known limits

- No login. A plan is reached by its number in the URL, so anyone who guesses it
  can open it. Add accounts before putting this online.
- `app.secret_key` is a placeholder and `debug=True` is on. Change both to deploy.
- Ratings, prices and popularity in `seed.py` are sample values. Practice links
  for Data Structures are real LeetCode problems; the other subjects use small
  tasks instead. Course links are search links.
- Three subjects (Data Structures, Web Development, Machine Learning), three
  topics each. Add more in `seed.py`.
