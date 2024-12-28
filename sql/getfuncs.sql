SELECT
    n.nspname AS schema_name,
    p.proname AS function_name,
    pg_catalog.pg_get_function_result(p.oid) AS return_type,
    pg_catalog.pg_get_function_arguments(p.oid) AS arguments,
    pg_catalog.pg_get_functiondef(p.oid) AS function_definition
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'your_schema_name'
ORDER BY schema_name, function_name;