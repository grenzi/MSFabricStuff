WITH table_list AS (
  SELECT 
    TABLE_SCHEMA as schema_name,
    TABLE_NAME as table_name,
    CASE 
      WHEN TABLE_NAME LIKE 'bronze_%' THEN REPLACE(TABLE_NAME, 'bronze_', 'silver_')
      WHEN TABLE_NAME LIKE 'bronze%' THEN CONCAT('silver', SUBSTRING(TABLE_NAME, 7))
      ELSE NULL
    END as potential_silver_name,
    CASE 
      WHEN TABLE_NAME LIKE 'silver_%' THEN REPLACE(TABLE_NAME, 'silver_', 'gold_')
      WHEN TABLE_NAME LIKE 'silver%' THEN CONCAT('gold', SUBSTRING(TABLE_NAME, 7))
      ELSE NULL
    END as potential_gold_name
  FROM 
    INFORMATION_SCHEMA.TABLES
  WHERE 
    TABLE_TYPE = 'BASE TABLE'
),
extended as (
SELECT 
  '['+schema_name+'].['+table_name+']' as selectable,
  table_name, 
  schema_name
FROM 
  table_list t1
WHERE 
  -- Original condition: bronze tables without silver or non-bronze tables
  (
    NOT EXISTS (
      SELECT 1
      FROM table_list t2
      WHERE 
        t2.schema_name = t1.schema_name
        AND t2.table_name = t1.potential_silver_name
    )
    OR t1.potential_silver_name IS NULL
  )
  -- New condition: silver tables without gold
  OR
  (
    NOT EXISTS (
      SELECT 1
      FROM table_list t3
      WHERE 
        t3.schema_name = t1.schema_name
        AND t3.table_name = t1.potential_gold_name
    )
    AND t1.potential_gold_name IS NOT NULL
  )
)
select * from extended
order by schema_name, replace(replace(replace(table_name, 'bronze_', ''), 'silver_', ''), 'gold_', '')
