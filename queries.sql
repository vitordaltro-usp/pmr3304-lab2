-- PMR3304 — Lab 2 — Seção 4: exercícios com SQL
-- Banco: db.sqlite3 (SQLite), populado com blog/fixtures/seed_data.json.
-- Exemplos: post de id 1 (tem comentários) e categoria "Tecnologia".
-- Observação: o Django grava as datas em UTC (horário de Brasília + 3 h).


-- 1. Todos os posts, ordenados pela data, do mais recente ao mais antigo.
SELECT *
FROM blog_post
ORDER BY pub_date DESC;


-- 2. Para um post com comentários (id 1), todos os seus comentários.
SELECT *
FROM blog_comment
WHERE post_id = 1;


-- 3. Para o mesmo post, todos os seus comentários com todas as colunas da
--    tabela de comentários (exceto post_id), o título do post e a sua data
--    de publicação, renomeada para post_date.
SELECT
    c.id,
    c.text,
    c.created_at,
    c.author_id,
    p.title,
    p.pub_date AS post_date
FROM blog_comment AS c
JOIN blog_post AS p ON p.id = c.post_id
WHERE c.post_id = 1;


-- 4. Para uma categoria (Tecnologia), todos os posts pertencentes a ela,
--    com as colunas da tabela de categoria e da tabela de posts.
--    A ligação muitos-para-muitos fica na tabela blog_post_categories.
SELECT
    cat.id AS category_id,
    cat.name,
    cat.description,
    p.id AS post_id,
    p.title,
    p.content,
    p.pub_date
FROM blog_category AS cat
JOIN blog_post_categories AS pc ON pc.category_id = cat.id
JOIN blog_post AS p ON p.id = pc.post_id
WHERE cat.name = 'Tecnologia';


-- 5. Todas as categorias que possuem dois ou mais posts.
SELECT
    cat.id,
    cat.name,
    cat.description,
    COUNT(pc.post_id) AS num_posts
FROM blog_category AS cat
JOIN blog_post_categories AS pc ON pc.category_id = cat.id
GROUP BY cat.id, cat.name, cat.description
HAVING COUNT(pc.post_id) >= 2;
