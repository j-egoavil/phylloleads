SELECT c.name, sp.platform, sp.username, sp.followers
FROM companies c
JOIN social_profiles sp ON c.id = sp.company_id;
SELECT c.name, c.email, ls.total_score, ls.priority
FROM companies c
JOIN lead_scores ls ON c.id = ls.company_id
ORDER BY ls.total_score DESC;
