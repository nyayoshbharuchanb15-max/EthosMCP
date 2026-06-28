-- Get all results for a session
SELECT * FROM phase_results WHERE session_id = :session_id ORDER BY phase_number;

-- Check for blocker fails
SELECT count(*) FROM phase_results 
WHERE session_id = :session_id 
AND (result_json->>'result' = 'BLOCKER_FAIL' OR (result_json->>'blocking')::boolean = true);

-- Get latest certificate
SELECT * FROM certificates WHERE session_id = :session_id ORDER BY issued_at DESC LIMIT 1;
