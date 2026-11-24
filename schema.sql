CREATE DATABASE IF NOT EXISTS studypath;
USE studypath;

CREATE TABLE IF NOT EXISTS subjects (
  subject_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS topics (
  topic_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL,
  name VARCHAR(150) NOT NULL,
  sequence_order INT NOT NULL,
  est_hours INT NOT NULL,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses (
  course_id INT AUTO_INCREMENT PRIMARY KEY,
  topic_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  platform VARCHAR(60) NOT NULL,
  url VARCHAR(400) NOT NULL,
  level ENUM('Beginner','Intermediate','Advanced') NOT NULL,
  rating DECIMAL(2,1) NOT NULL,
  is_free BOOLEAN NOT NULL,
  price_label VARCHAR(40) NOT NULL,
  popularity INT NOT NULL DEFAULT 50,
  FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- Practice problems for a topic (LeetCode-style where one exists, otherwise a small task).
CREATE TABLE IF NOT EXISTS questions (
  question_id INT AUTO_INCREMENT PRIMARY KEY,
  topic_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  difficulty ENUM('Easy','Medium','Hard') NOT NULL,
  url VARCHAR(400) NULL,
  FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- Multiple-choice quiz taken after a topic.
CREATE TABLE IF NOT EXISTS quiz_questions (
  quiz_id INT AUTO_INCREMENT PRIMARY KEY,
  topic_id INT NOT NULL,
  prompt VARCHAR(300) NOT NULL,
  option_a VARCHAR(200) NOT NULL,
  option_b VARCHAR(200) NOT NULL,
  option_c VARCHAR(200) NOT NULL,
  option_d VARCHAR(200) NOT NULL,
  correct_option CHAR(1) NOT NULL,
  FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- Who the plan belongs to. No login: name and education level are stored per plan.
CREATE TABLE IF NOT EXISTS learners (
  learner_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  education VARCHAR(30) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS study_plans (
  plan_id INT AUTO_INCREMENT PRIMARY KEY,
  learner_id INT NOT NULL,
  subject_id INT NOT NULL,
  level VARCHAR(20) NOT NULL,
  goal VARCHAR(30),
  budget VARCHAR(20) NOT NULL,
  hours_per_week INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (learner_id) REFERENCES learners(learner_id),
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- Course checklist ("I watched this"). Optional: topic completion comes from the quiz.
CREATE TABLE IF NOT EXISTS plan_items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  plan_id INT NOT NULL,
  course_id INT NOT NULL,
  week_no INT NOT NULL,
  done BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (plan_id) REFERENCES study_plans(plan_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- One row per (plan, topic) once the learner has attempted that topic's quiz.
CREATE TABLE IF NOT EXISTS topic_progress (
  progress_id INT AUTO_INCREMENT PRIMARY KEY,
  plan_id INT NOT NULL,
  topic_id INT NOT NULL,
  best_score INT NOT NULL DEFAULT 0,
  passed BOOLEAN NOT NULL DEFAULT FALSE,
  completed_at TIMESTAMP NULL,
  UNIQUE KEY one_row_per_topic (plan_id, topic_id),
  FOREIGN KEY (plan_id) REFERENCES study_plans(plan_id) ON DELETE CASCADE,
  FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- =====================================================================
-- Coding practice platform
-- =====================================================================

-- One row per coding problem. Examples, hints and discussion notes are stored as JSON text.
CREATE TABLE IF NOT EXISTS problems (
  problem_id INT AUTO_INCREMENT PRIMARY KEY,
  slug VARCHAR(80) NOT NULL UNIQUE,
  title VARCHAR(150) NOT NULL,
  difficulty VARCHAR(10) NOT NULL,
  pattern VARCHAR(80) NOT NULL,
  est_minutes INT NOT NULL,
  levels VARCHAR(60) NOT NULL,
  companies VARCHAR(200) NOT NULL DEFAULT '',
  statement TEXT NOT NULL,
  input_format TEXT NOT NULL,
  output_format TEXT NOT NULL,
  constraints_text TEXT NOT NULL,
  examples_json TEXT NOT NULL,
  hints_json TEXT NOT NULL,
  discussion_json TEXT NOT NULL,
  editorial TEXT NOT NULL,
  solution_code TEXT NOT NULL,
  time_limit_ms INT NOT NULL DEFAULT 2000,
  memory_limit_mb INT NOT NULL DEFAULT 256
);

-- Where a problem sits in each goal track: unit, priority (1 core, 2 important, 3 stretch), order.
CREATE TABLE IF NOT EXISTS problem_tracks (
  placement_id INT AUTO_INCREMENT PRIMARY KEY,
  problem_id INT NOT NULL,
  track VARCHAR(20) NOT NULL,
  unit_no INT NOT NULL,
  unit_name VARCHAR(80) NOT NULL,
  priority INT NOT NULL,
  seq INT NOT NULL,
  UNIQUE KEY one_placement (problem_id, track),
  FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
);

-- Public cases are shown to the learner. Hidden cases are only ever reported as pass or fail.
CREATE TABLE IF NOT EXISTS test_cases (
  test_id INT AUTO_INCREMENT PRIMARY KEY,
  problem_id INT NOT NULL,
  ordinal INT NOT NULL,
  is_public BOOLEAN NOT NULL,
  input_text MEDIUMTEXT NOT NULL,
  expected_text MEDIUMTEXT NOT NULL,
  FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
);

-- A learner's personalised roadmap. No login: the path id in the URL is the key.
CREATE TABLE IF NOT EXISTS paths (
  path_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  role VARCHAR(40) NOT NULL,
  level VARCHAR(20) NOT NULL,
  goal VARCHAR(40) NOT NULL,
  track VARCHAR(20) NOT NULL,
  language VARCHAR(20) NOT NULL,
  deadline_days INT NOT NULL,
  minutes_per_day INT NOT NULL,
  start_date VARCHAR(10) NOT NULL,
  last_replan_day INT NOT NULL DEFAULT 0,
  plan_note TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The day-by-day schedule. status: pending (scheduled), done (solved), backlog (parked to protect the deadline).
CREATE TABLE IF NOT EXISTS path_items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  path_id INT NOT NULL,
  problem_id INT NOT NULL,
  curriculum_order INT NOT NULL,
  day_no INT NULL,
  status VARCHAR(10) NOT NULL DEFAULT 'pending',
  hints_used INT NOT NULL DEFAULT 0,
  solved_at VARCHAR(19) NULL,
  UNIQUE KEY one_item_per_problem (path_id, problem_id),
  FOREIGN KEY (path_id) REFERENCES paths(path_id) ON DELETE CASCADE,
  FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

CREATE TABLE IF NOT EXISTS submissions (
  submission_id INT AUTO_INCREMENT PRIMARY KEY,
  path_id INT NOT NULL,
  problem_id INT NOT NULL,
  language VARCHAR(20) NOT NULL,
  code MEDIUMTEXT NOT NULL,
  verdict VARCHAR(30) NOT NULL,
  passed INT NOT NULL DEFAULT 0,
  total INT NOT NULL DEFAULT 0,
  runtime_ms INT NULL,
  memory_mb DECIMAL(8,1) NULL,
  created_at VARCHAR(19) NOT NULL,
  FOREIGN KEY (path_id) REFERENCES paths(path_id) ON DELETE CASCADE,
  FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);

-- The learner's private notes on a problem (autosaved from the workspace).
CREATE TABLE IF NOT EXISTS problem_notes (
  note_id INT AUTO_INCREMENT PRIMARY KEY,
  path_id INT NOT NULL,
  problem_id INT NOT NULL,
  body TEXT NOT NULL,
  updated_at VARCHAR(19) NOT NULL,
  UNIQUE KEY one_note_per_problem (path_id, problem_id),
  FOREIGN KEY (path_id) REFERENCES paths(path_id) ON DELETE CASCADE,
  FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
);