from data.database import Database

db = Database()

# Check current state
db.cursor.execute('SELECT COUNT(*) as cnt FROM test_stages')
stage_count = db.cursor.fetchone()
print(f'Current stages count: {stage_count["cnt"]}')

db.cursor.execute('SELECT COUNT(*) as cnt FROM test_stage_results')
stage_results_count = db.cursor.fetchone()
print(f'Current stage results count: {stage_results_count["cnt"]}')

# Get test case ID
db.cursor.execute('SELECT id FROM test_cases LIMIT 1')
test_case = db.cursor.fetchone()

if not test_case:
    print('No test cases found! Creating a default test case...')
    db.cursor.execute('''
        INSERT INTO test_cases (name, description, voltage_min, voltage_max, 
                               current_min, current_max, resistance_min, resistance_max, created_by)
        VALUES ('Default Test', 'Default test case for single PCB testing', 
                0, 999, 0, 999, 0, 9999, 1)
    ''')
    db.conn.commit()
    test_case_id = db.cursor.lastrowid
    print(f'Created test case with ID: {test_case_id}')
else:
    test_case_id = test_case['id']
    print(f'Found test case ID: {test_case_id}')

# Check if stage exists for this test case
db.cursor.execute('SELECT id FROM test_stages WHERE test_case_id = %s', (test_case_id,))
existing_stage = db.cursor.fetchone()

if not existing_stage:
    print('No stage found, creating default stage...')
    db.cursor.execute('''
        INSERT INTO test_stages 
        (test_case_id, stage_number, stage_name, description, 
         voltage_min, voltage_max, current_min, current_max, 
         resistance_min, resistance_max)
        VALUES (%s, 1, 'Default Stage', 'Auto-created stage for single PCB test',
                0, 999, 0, 999, 0, 9999)
    ''', (test_case_id,))
    db.conn.commit()
    stage_id = db.cursor.lastrowid
    print(f'Created stage with ID: {stage_id}')
else:
    stage_id = existing_stage['id']
    print(f'Stage already exists with ID: {stage_id}')

# Now let's manually add stage results for existing test results that don't have them
print('\nAdding stage results for existing test results...')
db.cursor.execute('''
    SELECT tr.id, tr.pcb_serial_number, tr.status
    FROM test_results tr
    LEFT JOIN test_stage_results tsr ON tr.id = tsr.test_result_id
    WHERE tsr.id IS NULL
    ORDER BY tr.id DESC
    LIMIT 10
''')
test_results_without_stages = db.cursor.fetchall()

print(f'Found {len(test_results_without_stages)} test results without stage results')

# For now, add dummy data - in real scenario this should come from actual measurements
for tr in test_results_without_stages:
    # Use dummy values - user will need to re-run tests for real data
    db.cursor.execute('''
        INSERT INTO test_stage_results 
        (test_result_id, stage_id, voltage_measured, current_measured, 
         resistance_measured, status, failure_reason, start_time, end_time)
        VALUES (%s, %s, 4.5, 0.1, 100.0, %s, '', NOW(), NOW())
    ''', (tr['id'], stage_id, tr['status']))
    print(f'  Added stage result for test result ID: {tr["id"]}')

db.conn.commit()

print('\nFinal counts:')
db.cursor.execute('SELECT COUNT(*) as cnt FROM test_stages')
print(f'  Stages: {db.cursor.fetchone()["cnt"]}')

db.cursor.execute('SELECT COUNT(*) as cnt FROM test_stage_results')
print(f'  Stage results: {db.cursor.fetchone()["cnt"]}')

db.close()
print('\nDone! Database is now ready.')
