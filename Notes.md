# Notes

```sql
select * from public.markers m
where st_contains((
	select location::geometry from public.regions r
	where name = 'Jaguara'
), point::geometry)
```

Permite verificar se um ponto está dentro de uma região.