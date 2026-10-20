-- Списки и фильтрация (WHERE)
-- 1. Все мудборды дизайнера
SELECT * FROM moodboards WHERE designer_id = ? ORDER BY updated_at DESC;

-- 2. Мудборды с указанным цветом фона
SELECT id, title FROM moodboards WHERE background_color = ?;

-- Связанные данные (JOIN)
-- 3. Мудборды с каталогами
SELECT m.title, c.name AS catalog_name
FROM moodboards AS m
JOIN catalogs AS c ON c.id = m.catalog_id;

-- 4. Мудборды с заказчиками
SELECT m.title, cl.name AS client_name, cl.email
FROM moodboards AS m
JOIN clients AS cl ON cl.id = m.client_id;

-- 5. Полная карточка мудборда
SELECT m.*, d.display_name, c.name AS catalog_name, cl.name AS client_name
FROM moodboards AS m
JOIN designers AS d ON d.id = m.designer_id
LEFT JOIN catalogs AS c ON c.id = m.catalog_id
LEFT JOIN clients AS cl ON cl.id = m.client_id
WHERE m.id = ?;

-- Агрегатные функции
-- 6. Общее количество мудбордов
SELECT COUNT(*) AS moodboard_count FROM moodboards;

-- 7. Среднее количество палитр на мудборд
SELECT AVG(palette_count) AS average_palette_size
FROM (
    SELECT moodboard_id, COUNT(*) AS palette_count
    FROM palette_colors
    GROUP BY moodboard_id
);

-- Группировка
-- 8. Количество мудбордов по дизайнеру
SELECT d.display_name, COUNT(m.id) AS moodboard_count
FROM designers AS d
LEFT JOIN moodboards AS m ON m.designer_id = d.id
GROUP BY d.id, d.display_name;

-- 9. Количество мудбордов по каталогу
SELECT c.name, COUNT(m.id) AS moodboard_count
FROM catalogs AS c
LEFT JOIN moodboards AS m ON m.catalog_id = c.id
GROUP BY c.id, c.name;

-- 10. Каталоги с двумя и более мудбордами (HAVING)
SELECT c.name, COUNT(m.id) AS moodboard_count
FROM catalogs AS c
LEFT JOIN moodboards AS m ON m.catalog_id = c.id
GROUP BY c.id, c.name
HAVING COUNT(m.id) >= ?;

-- 11. Поиск по части названия с параметром
SELECT id, title FROM moodboards WHERE title LIKE ? ORDER BY title;

-- 12. Последние мудборды с ограничением выборки
SELECT id, title, updated_at FROM moodboards
ORDER BY updated_at DESC LIMIT ? OFFSET ?;
