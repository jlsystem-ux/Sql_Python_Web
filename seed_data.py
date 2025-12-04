"""
Seed data for SQL for Testers - QA-Focused Database
Populates the database with realistic testing/QA data
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

DB_NAME = 'database.db'

def seed_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Read and execute schema
    with open('schema_v2.sql', 'r') as f:
        schema_sql = f.read()
        cur.executescript(schema_sql)
    
    print("[OK] Schema created")
    
    # ============================================
    # SEED USERS
    # ============================================
    users_data = [
        ('john.doe@example.com', 'John', 'Doe', '123 Main St', '12345', 'New York', 'NY', 'USA', '555-0100'),
        ('jane.smith@example.com', 'Jane', 'Smith', '456 Oak Ave', '67890', 'Los Angeles', 'CA', 'USA', '555-0101'),
        ('bob.johnson@example.com', 'Bob', 'Johnson', '789 Pine Rd', '11111', 'Chicago', 'IL', 'USA', '555-0102'),
    ]
    
    hashed_password = generate_password_hash('password123')
    for user in users_data:
        cur.execute("""
            INSERT INTO users (email, password, firstName, lastName, address1, zipcode, city, state, country, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user[0], hashed_password, user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8]))
    
    print("[OK] Users seeded (password: password123)")
    
    # ============================================
    # SEED DEPARTMENTS
    # ============================================
    departments_data = [
        ('Engineering', 'San Francisco', 500000),
        ('Quality Assurance', 'Austin', 300000),
        ('Product Management', 'New York', 400000),
        ('DevOps', 'Seattle', 350000),
        ('Customer Support', 'Remote', 200000),
    ]
    
    for dept in departments_data:
        cur.execute("INSERT INTO departments (department_name, location, budget) VALUES (?, ?, ?)", dept)
    
    print("[OK] Departments seeded")
    
    # ============================================
    # SEED EMPLOYEES
    # ============================================
    employees_data = [
        ('Alice', 'Anderson', 'alice.anderson@company.com', 1, 95000, '2020-01-15', None, 'Senior Software Engineer'),
        ('Carlos', 'Martinez', 'carlos.martinez@company.com', 1, 105000, '2019-03-20', 1, 'Lead Software Engineer'),
        ('Diana', 'Chen', 'diana.chen@company.com', 2, 75000, '2021-06-01', None, 'QA Engineer'),
        ('Ethan', 'Brown', 'ethan.brown@company.com', 2, 85000, '2020-09-10', 3, 'Senior QA Engineer'),
        ('Fatima', 'Hassan', 'fatima.hassan@company.com', 2, 80000, '2021-02-14', 4, 'QA Automation Engineer'),
        ('George', 'Kim', 'george.kim@company.com', 3, 110000, '2018-07-01', None, 'Product Manager'),
        ('Hannah', 'Lee', 'hannah.lee@company.com', 4, 90000, '2020-11-05', None, 'DevOps Engineer'),
        ('Isaac', 'Patel', 'isaac.patel@company.com', 4, 95000, '2019-12-12', 7, 'Senior DevOps Engineer'),
        ('Julia', 'Rodriguez', 'julia.rodriguez@company.com', 5, 60000, '2022-01-10', None, 'Support Engineer'),
        ('Kevin', 'Wang', 'kevin.wang@company.com', 1, 92000, '2021-04-22', 2, 'Software Engineer'),
    ]
    
    for emp in employees_data:
        cur.execute("""
            INSERT INTO employees (first_name, last_name, email, department_id, salary, hire_date, manager_id, job_title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, emp)
    
    print("[OK] Employees seeded")
    
    # ============================================
    # SEED PROJECTS
    # ============================================
    projects_data = [
        ('Mobile App Redesign', 'Redesign of iOS and Android apps', '2024-01-01', '2024-06-30', 250000, 'Active', 1),
        ('API Performance Optimization', 'Improve API response times', '2024-02-15', '2024-05-15', 150000, 'Active', 1),
        ('Customer Portal V2', 'New customer self-service portal', '2023-10-01', '2024-03-31', 300000, 'Completed', 3),
        ('Automated Testing Framework', 'Build comprehensive test automation', '2024-01-10', '2024-12-31', 200000, 'Active', 2),
        ('Database Migration', 'Migrate from MySQL to PostgreSQL', '2024-03-01', '2024-07-31', 180000, 'Active', 4),
    ]
    
    for proj in projects_data:
        cur.execute("""
            INSERT INTO projects (project_name, description, start_date, end_date, budget, status, department_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, proj)
    
    print("[OK] Projects seeded")
    
    # ============================================
    # SEED EMPLOYEE_PROJECTS
    # ============================================
    employee_projects_data = [
        (1, 1, 'Developer', 320),
        (2, 1, 'Tech Lead', 280),
        (3, 1, 'QA Tester', 240),
        (4, 1, 'QA Lead', 200),
        (5, 4, 'Automation Engineer', 400),
        (6, 1, 'Product Manager', 150),
        (7, 5, 'DevOps Lead', 350),
        (10, 2, 'Developer', 280),
    ]
    
    for ep in employee_projects_data:
        cur.execute("""
            INSERT INTO employee_projects (employee_id, project_id, role, hours_worked)
            VALUES (?, ?, ?, ?)
        """, ep)
    
    print("[OK] Employee-Project relationships seeded")
    
    # ============================================
    # SEED TEST_RESULTS
    # ============================================
    test_statuses = ['Passed', 'Failed', 'Skipped', 'Blocked']
    test_suites = ['Smoke Tests', 'Regression Tests', 'Integration Tests', 'E2E Tests', 'API Tests']
    
    base_date = datetime(2024, 1, 1)
    for i in range(50):
        test_date = base_date + timedelta(days=random.randint(0, 120))
        cur.execute("""
            INSERT INTO test_results (test_name, test_status, execution_date, tester_id, project_id, bug_count, execution_time_ms, test_suite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f'Test_{i+1:03d}',
            random.choice(test_statuses),
            test_date.strftime('%Y-%m-%d %H:%M:%S'),
            random.choice([3, 4, 5]),  # QA employees
            random.choice([1, 2, 3, 4]),
            random.randint(0, 5),
            random.randint(100, 5000),
            random.choice(test_suites)
        ))
    
    print("[OK] Test results seeded")
    
    # ============================================
    # SEED BUGS
    # ============================================
    severities = ['Critical', 'High', 'Medium', 'Low']
    priorities = ['Urgent', 'High', 'Medium', 'Low']
    statuses = ['Open', 'In Progress', 'Fixed', 'Closed', 'Wont Fix']
    
    bug_titles = [
        'Login page crashes on iOS',
        'Payment processing timeout',
        'Database connection pool exhausted',
        'Memory leak in background service',
        'Incorrect calculation in reports',
        'API returns 500 on large payloads',
        'UI text overlap on mobile',
        'Search function returns duplicates',
        'Session not persisting',
        'Email notifications not sent',
        'Export to CSV fails',
        'Date picker shows wrong timezone',
        'Profile image upload fails',
        'Pagination broken on last page',
        'Dashboard charts not loading',
    ]
    
    for i, title in enumerate(bug_titles, 1):
        reported_date = base_date + timedelta(days=random.randint(0, 100))
        status = random.choice(statuses)
        fixed_date = None
        if status in ['Fixed', 'Closed']:
            fixed_date = (reported_date + timedelta(days=random.randint(1, 20))).strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute("""
            INSERT INTO bugs (bug_title, bug_description, severity, priority, status, reported_by, assigned_to, reported_date, fixed_date, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            f'Detailed description for {title}',
            random.choice(severities),
            random.choice(priorities),
            status,
            random.choice([3, 4, 5]),  # QA employees
            random.choice([1, 2, 10]),  # Dev employees
            reported_date.strftime('%Y-%m-%d %H:%M:%S'),
            fixed_date,
            random.choice([1, 2, 3, 4])
        ))
    
    print("[OK] Bugs seeded")
    
    # ============================================
    # SEED TEST_ENVIRONMENTS
    # ============================================
    environments = [
        ('Windows 11 + Chrome', 'Windows 11', 'Chrome', '120.0', 1),
        ('macOS + Safari', 'macOS Sonoma', 'Safari', '17.2', 1),
        ('Linux + Firefox', 'Ubuntu 22.04', 'Firefox', '121.0', 2),
        ('Mobile Android', 'Android 14', 'Chrome Mobile', '120.0', 1),
        ('Mobile iOS', 'iOS 17', 'Safari Mobile', '17.2', 1),
    ]
    
    for env in environments:
        cur.execute("""
            INSERT INTO test_environments (env_name, os, browser, browser_version, project_id)
            VALUES (?, ?, ?, ?, ?)
        """, env)
    
    print("[OK] Test environments seeded")
    
    conn.commit()
    conn.close()
    
    print("\n[SUCCESS] Database seeded successfully!")
    print("=" * 50)
    print("Test user credentials:")
    print("  Email: john.doe@example.com")
    print("  Password: password123")
    print("=" * 50)

if __name__ == '__main__':
    seed_database()
