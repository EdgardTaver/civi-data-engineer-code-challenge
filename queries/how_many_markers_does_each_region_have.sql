SELECT region, count(region)
FROM dwh.markers u 
WHERE region IS NOT NULL
GROUP BY region
ORDER BY 2 DESC