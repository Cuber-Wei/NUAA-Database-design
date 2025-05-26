-- t1 建立男学生的视图，属性包括学号、姓名、选修课程名和成绩。
CREATE VIEW MaleStudents AS
SELECT S.Sno, S.Sname, C.Cname, SC.Grade
FROM S
JOIN SC ON S.Sno = SC.Sno
JOIN C ON SC.Cno = C.Cno
WHERE S.Ssex = '男';

-- t2 在男学生视图中查询平均成绩大于 80 分的学生学号与姓名。
SELECT Sno, Sname
FROM MaleStudents
GROUP BY Sno, Sname
HAVING AVG(Grade) > 80;
