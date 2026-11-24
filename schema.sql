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
