-- Canonical relational schema — Adaptive Exam-Prep Platform (System Design §3)
-- PostgreSQL 16. jsonb for flexible item payloads; attempts/answer_marks append-only.

-- ---------- Identity & roles ----------
CREATE TABLE accounts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email           citext UNIQUE NOT NULL,
  billing_customer_id text,
  country         text,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TYPE user_role AS ENUM ('student','parent','tutor','teacher','admin');

CREATE TABLE user_profiles (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id    uuid REFERENCES accounts(id),
  role          user_role NOT NULL,
  display_name  text,
  dob           date,
  year_group    int,
  avatar        text,
  locale        text,
  status        text NOT NULL DEFAULT 'active'
);

CREATE TABLE guardian_links (
  parent_id    uuid REFERENCES user_profiles(id),
  student_id   uuid REFERENCES user_profiles(id),
  consent_id   uuid,
  relationship text,
  PRIMARY KEY (parent_id, student_id)
);

CREATE TYPE org_type AS ENUM ('school','agency');
CREATE TABLE orgs (
  id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type      org_type NOT NULL,
  name      text NOT NULL,
  plan_tier text,
  region    text
);

CREATE TABLE memberships (
  org_id   uuid REFERENCES orgs(id),
  user_id  uuid REFERENCES user_profiles(id),
  role     text,
  class_id uuid,
  PRIMARY KEY (org_id, user_id)
);

-- ---------- Content (versioned) ----------
CREATE TYPE exam_stage AS ENUM ('ks2','11plus','iseb','cat4','gcse');
CREATE TABLE subjects (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name       text NOT NULL,
  exam_stage exam_stage NOT NULL
);

CREATE TABLE topics (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id     uuid REFERENCES subjects(id),
  name           text NOT NULL,
  parent_topic_id uuid REFERENCES topics(id),
  order_idx      int
);

CREATE TABLE skills (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  topic_id   uuid REFERENCES topics(id),
  code       text,
  descriptor text
);

CREATE TYPE question_type AS ENUM ('mcq','numeric','cloze','short','long');
CREATE TYPE question_status AS ENUM ('draft','review','live','retired');
CREATE TABLE questions (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id        uuid REFERENCES skills(id),
  type            question_type NOT NULL,
  body            jsonb NOT NULL,
  assets          jsonb,
  exam_board      text[],
  difficulty_b    numeric,        -- IRT difficulty
  discrimination_a numeric,       -- IRT discrimination
  status          question_status NOT NULL DEFAULT 'draft',
  version         int NOT NULL DEFAULT 1,
  author_id       uuid REFERENCES user_profiles(id),
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE mark_scheme_items (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id  uuid REFERENCES questions(id),
  marks        int NOT NULL,
  criterion    text NOT NULL,
  accept       jsonb,
  reject       jsonb,
  model_answer text
);

-- ---------- Activity (append-only) ----------
CREATE TYPE session_kind AS ENUM ('practice','mock','assignment','baseline');
CREATE TABLE sessions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id  uuid REFERENCES user_profiles(id),
  kind        session_kind NOT NULL,
  exam_board  text,
  started_at  timestamptz NOT NULL DEFAULT now(),
  ended_at    timestamptz,
  time_limit_s int,
  status      text
);

CREATE TABLE attempts (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id   uuid REFERENCES sessions(id),
  question_id  uuid REFERENCES questions(id),
  presented_at timestamptz,
  answered_at  timestamptz,
  response     jsonb,
  time_taken_ms int,
  seq          int
);  -- append-only: corrections add rows, never UPDATE

CREATE TYPE marker_kind AS ENUM ('auto','ml','human');
CREATE TABLE answer_marks (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  attempt_id          uuid REFERENCES attempts(id),
  mark_scheme_item_id uuid REFERENCES mark_scheme_items(id),
  awarded             int NOT NULL,
  max                 int NOT NULL,
  rationale           text,
  marker              marker_kind NOT NULL,
  confidence          numeric
);

-- ---------- Learner model & analytics ----------
CREATE TABLE skill_mastery (
  student_id   uuid REFERENCES user_profiles(id),
  skill_id     uuid REFERENCES skills(id),
  theta        numeric,
  se           numeric,
  attempts     int NOT NULL DEFAULT 0,
  last_seen_at timestamptz,
  PRIMARY KEY (student_id, skill_id)
);

CREATE TABLE plans (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id   uuid REFERENCES user_profiles(id),
  exam_date    date,
  generated_at timestamptz NOT NULL DEFAULT now(),
  strategy     jsonb
);

CREATE TYPE plan_item_status AS ENUM ('todo','doing','done');
CREATE TABLE plan_items (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id        uuid REFERENCES plans(id),
  week           int,
  skill_id       uuid REFERENCES skills(id),
  target_minutes int,
  status         plan_item_status NOT NULL DEFAULT 'todo',
  assignment_id  uuid
);

CREATE TABLE progress_snapshots (
  student_id  uuid REFERENCES user_profiles(id),
  period      date,
  mastery_avg numeric,
  minutes     int,
  accuracy    numeric,
  on_track    boolean,
  PRIMARY KEY (student_id, period)
);

-- ---------- Billing ----------
CREATE TABLE subscriptions (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id         uuid REFERENCES accounts(id),
  stripe_sub_id      text,
  tier               text,
  status             text,
  trial_ends_at      timestamptz,
  current_period_end timestamptz,
  seats              int
);

CREATE TABLE entitlements (
  account_id  uuid REFERENCES accounts(id),
  feature     text,
  limit_value int,
  source      text   -- 'plan' | 'grant'
);

-- ---------- Safety & audit ----------
CREATE TABLE consents (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  granter_user_id uuid REFERENCES user_profiles(id),
  subject_user_id uuid REFERENCES user_profiles(id),
  type            text,
  granted_at      timestamptz NOT NULL DEFAULT now(),
  evidence        text
);

CREATE TABLE audit_log (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id uuid,
  action        text,
  target_type   text,
  target_id     uuid,
  at            timestamptz NOT NULL DEFAULT now(),
  ip            text,
  meta          jsonb
);
