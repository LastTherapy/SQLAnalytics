SELECT
    c.table_schema,
    c.table_name,
    array_agg(c.column_name::text) AS column_names,
    array_agg(c.data_type::text) AS data_types
FROM information_schema.columns c
WHERE c.table_schema = 'your_schema_name'
  AND c.table_name NOT IN (
      SELECT c.relname
      FROM pg_inherits i
      JOIN pg_class c ON i.inhrelid = c.oid
  )
GROUP BY c.table_schema, c.table_name;
