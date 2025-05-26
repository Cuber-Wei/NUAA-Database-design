-- t1 查询选修1号课程的学生学号与姓名
SELECT S.Sno, S.Sname
FROM S
JOIN SC ON S.Sno = SC.Sno
WHERE SC.Cno = '81001';

-- t2 查询选修课程名为数据结构的学生学号与姓名
SELECT S.Sno, S.Sname
FROM S
JOIN SC ON S.Sno = SC.Sno
JOIN C ON SC.Cno = C.Cno
WHERE C.Cname = '数据结构';

-- t3 查询不选1号课程的学生学号与姓名
SELECT S.Sno, S.Sname
FROM S
WHERE NOT EXISTS (
    SELECT 1 FROM SC
    WHERE SC.Sno = S.Sno AND SC.Cno = '81001'
);

-- t4 查询学习全部课程的学生姓名
SELECT S.Sname
FROM S
WHERE NOT EXISTS (
    SELECT C.Cno FROM C
    WHERE NOT EXISTS (
        SELECT 1 FROM SC
        WHERE SC.Sno = S.Sno AND SC.Cno = C.Cno
    )
);

-- t5 查询所有学生除了选修1号课程外所有成绩均及格的学生学号和平均成绩，并将结果按平均成绩降序排列
SELECT S.Sno, AVG(SC.Grade) AS AvgGrade
FROM S
JOIN SC ON S.Sno = SC.Sno
WHERE NOT EXISTS (
    SELECT 1
    FROM SC AS SC2
    WHERE SC2.Sno = S.Sno
    AND SC2.Cno <> '1'
    AND SC2.Grade < 60
)
GROUP BY S.Sno
ORDER BY AvgGrade DESC;

-- t6 查询选修数据库原理成绩第 2 名的学生姓名。
WITH RankedGrades AS (
    SELECT S.Sname, SC.Grade,
           DENSE_RANK() OVER (ORDER BY SC.Grade DESC) AS drank
    FROM SC
    JOIN C ON SC.Cno = C.Cno
    JOIN S ON SC.Sno = S.Sno
    WHERE C.Cname = '数据库原理'
)
SELECT Sname
FROM RankedGrades
WHERE drank = 2;

-- t7 查询所有 3 个学分课程中有 3 门以上（含 3 门）课程获 80 分以上（含 80分）的学生的姓名。
SELECT S.Sname
FROM S
JOIN SC ON S.Sno = SC.Sno
JOIN C ON SC.Cno = C.Cno
WHERE C.Ccredit = 3 AND SC.Grade >= 80
GROUP BY S.Sno, S.Sname
HAVING COUNT(DISTINCT C.Cno) >= 3;

-- t8 查询选课门数唯一的学生的学号。
WITH CourseCount AS (
    SELECT Sno, COUNT(*) AS num
    FROM SC
    GROUP BY Sno
)
SELECT Sno
FROM CourseCount
WHERE num IN (
    SELECT num
    FROM CourseCount
    GROUP BY num
    HAVING COUNT(*) = 1
);
