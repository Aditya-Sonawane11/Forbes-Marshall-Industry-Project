SELECT
    tr.id AS test_result_id,
    tr.pcb_serial_number,
    tr.status AS test_status,
    tr.overall_pass,
    tr.start_time AS test_start,
    tr.end_time AS test_end,
    tr.notes AS test_notes,

    -- User Information
    u.id AS user_id,
    u.username,
    u.role AS user_role,
    u.email AS user_email,

    -- Test Case Information
    tc.id AS test_case_id,
    tc.name AS test_case_name,
    tc.description AS test_case_description,
    tc.voltage_min AS tc_voltage_min,
    tc.voltage_max AS tc_voltage_max,
    tc.current_min AS tc_current_min,
    tc.current_max AS tc_current_max,
    tc.resistance_min AS tc_res_min,
    tc.resistance_max AS tc_res_max,

    -- Test Stage Results
    tsr.id AS stage_result_id,
    ts.stage_number,
    ts.stage_name,
    ts.description AS stage_description,
    tsr.voltage_measured,
    tsr.current_measured,
    tsr.resistance_measured,
    tsr.status AS stage_status,
    tsr.failure_reason,
    tsr.start_time AS stage_start_time,
    tsr.end_time AS stage_end_time,

    -- Jig Diagram (if mapped to the test case)
    jd.diagram_name,
    jd.file_path AS jig_diagram_path,
    jd.description AS jig_description,

    -- Communication Configuration
    cc.config_name AS comm_config_name,
    cc.com_port,
    cc.baud_rate,
    cc.data_bits,
    cc.stop_bits,
    cc.parity,
    cc.timeout_seconds AS comm_timeout,

    -- Test Statistics
    tsx.total_tests,
    tsx.passed_tests,
    tsx.failed_tests,
    tsx.pass_rate,

    -- Audit Log Info
    al.action AS audit_action,
    al.entity_type AS audit_entity_type,
    al.entity_id AS audit_entity_id,
    al.timestamp AS audit_timestamp

FROM test_results tr
JOIN users u ON tr.user_id = u.id
JOIN test_cases tc ON tr.test_case_id = tc.id

-- Stage results
LEFT JOIN test_stage_results tsr ON tsr.test_result_id = tr.id
LEFT JOIN test_stages ts ON ts.id = tsr.stage_id

-- Jig diagrams linked with test cases
LEFT JOIN jig_diagrams jd ON jd.test_case_id = tc.id

-- Communication configuration (not always linked; joining user who created config)
LEFT JOIN communication_config cc ON cc.created_by = u.id

-- Test statistics
LEFT JOIN test_statistics tsx ON tsx.test_case_id = tc.id

-- Audit logs for the user
LEFT JOIN audit_log al ON al.user_id = u.id

ORDER BY tr.start_time DESC, ts.stage_number ASC;