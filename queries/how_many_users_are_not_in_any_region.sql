SELECT COUNT(id) AS users_not_in_any_region FROM dwh.users
WHERE 1=1
AND deleted_at IS NULL
AND region IS NULL