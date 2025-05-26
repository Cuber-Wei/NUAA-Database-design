-- t1 计算每个学生有成绩的课程门数、平均成绩。
SELECT S.Sno, S.Sname, COUNT(SC.Cno) AS CourseCount, AVG(SC.Grade) AS AvgGrade
FROM S
JOIN SC ON S.Sno = SC.Sno
GROUP BY S.Sno, S.Sname;

-- t2 使用 GRANT 语句，把对基本表 S、SC、C 的使用权限授给其它用户。
GRANT SELECT, INSERT, UPDATE, DELETE ON S TO 'other_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON SC TO 'other_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON C TO 'other_user'@'localhost';

-- t3 实验完成后，撤消建立的基本表和视图。
DROP VIEW IF EXISTS MaleStudents;
DROP TABLE IF EXISTS SC;
DROP TABLE IF EXISTS C;
DROP TABLE IF EXISTS S;

CREATE USER 'other_user'@'localhost' IDENTIFIED BY 'Wei-951231';