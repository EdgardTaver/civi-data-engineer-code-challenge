WITH params AS (SELECT 5 AS N)
SELECT region, count(region) FROM dwh.users
WHERE 1=1
	AND deleted_at IS NULL
	AND region IS NOT NULL 
GROUP BY region
ORDER BY 2 DESC
LIMIT (SELECT N FROM params)