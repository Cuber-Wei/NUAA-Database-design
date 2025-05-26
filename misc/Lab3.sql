-- t1 把 1 号课程的非空成绩提高 10％。
UPDATE SC
SET Grade = Grade * 1.1
WHERE Cno = '81001' AND Grade IS NOT NULL;

-- t2 在 SC 表中删除课程名为数据结构的成绩的元组。
DELETE FROM SC
WHERE Cno IN (
    SELECT Cno FROM C
    WHERE Cname = '数据结构'
);

-- t3 在 S 和 SC 表中删除学号为 202415122 的所有数据。
DELETE FROM SC
WHERE Sno = '202415122';
DELETE FROM S
WHERE Sno = '202415122';
