-- SQL for Testers - QA-Focused Database Schema
-- Version 2.0 - Learning Platform

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    address1 TEXT,
    zipcode TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    phone TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Track user progress through lessons
CREATE TABLE IF NOT EXISTS user_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    lesson_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    attempts INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(userId),
    UNIQUE(user_id, lesson_id, exercise_id)
);

-- User badges/achievements
CREATE TABLE IF NOT EXISTS user_badges (
    badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_name TEXT NOT NULL,
    badge_description TEXT,
    earned_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(userId)
);

-- ============================================
-- QA/TESTING FOCUSED TABLES
-- ============================================

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL,
    location TEXT,
    budget REAL
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    department_id INTEGER,
    salary REAL,
    hire_date TEXT,
    manager_id INTEGER,
    job_title TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT,
    start_date TEXT,
    end_date TEXT,
    budget REAL,
    status TEXT CHECK(status IN ('Planning', 'Active', 'On Hold', 'Completed', 'Cancelled')),
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Employee_Projects (many-to-many relationship)
CREATE TABLE IF NOT EXISTS employee_projects (
    employee_id INTEGER,
    project_id INTEGER,
    role TEXT,
    hours_worked INTEGER DEFAULT 0,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Test_Results (QA-specific)
CREATE TABLE IF NOT EXISTS test_results (
    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    test_status TEXT CHECK(test_status IN ('Passed', 'Failed', 'Skipped', 'Blocked')),
    execution_date TEXT,
    tester_id INTEGER,
    project_id INTEGER,
    bug_count INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    test_suite TEXT,
    FOREIGN KEY (tester_id) REFERENCES employees(employee_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Bugs table
CREATE TABLE IF NOT EXISTS bugs (
    bug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_title TEXT NOT NULL,
    bug_description TEXT,
    severity TEXT CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')),
    priority TEXT CHECK(priority IN ('Urgent', 'High', 'Medium', 'Low')),
    status TEXT CHECK(status IN ('Open', 'In Progress', 'Fixed', 'Closed', 'Wont Fix')),
    reported_by INTEGER,
    assigned_to INTEGER,
    reported_date TEXT DEFAULT (datetime('now')),
    fixed_date TEXT,
    project_id INTEGER,
    FOREIGN KEY (reported_by) REFERENCES employees(employee_id),
    FOREIGN KEY (assigned_to) REFERENCES employees(employee_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- Test Environments
CREATE TABLE IF NOT EXISTS test_environments (
    env_id INTEGER PRIMARY KEY AUTOINCREMENT,
    env_name TEXT NOT NULL,
    os TEXT,
    browser TEXT,
    browser_version TEXT,
    project_id INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_projects_dept ON projects(department_id);
CREATE INDEX IF NOT EXISTS idx_test_results_project ON test_results(project_id);
CREATE INDEX IF NOT EXISTS idx_test_results_tester ON test_results(tester_id);
CREATE INDEX IF NOT EXISTS idx_bugs_project ON bugs(project_id);
CREATE INDEX IF NOT EXISTS idx_bugs_assigned ON bugs(assigned_to);
CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id);
