create database if not exists teach_db;

use teach_db;

-- Table1: Students
create table if not exists S
(
    Sno varchar(20) primary key comment "学号",
    Sname varchar(20) not null comment "姓名", 
    Ssex varchar(1) not null comment "性别",
    Sbirthdate date not null comment "出生日期",
    Sdept varchar(20) not null comment "主修专业"
) comment "学生" collate = utf8mb4_unicode_ci;

-- Table2: Courses
create table if not exists C
(
    Cno varchar(20) primary key comment "课程号",
    Cname varchar(20) not null comment "课程名",
    Cpno varchar(20) comment "先行课",
    Ccredict int not null comment "学分"
) comment "课程" collate = utf8mb4_unicode_ci;

-- Table3: Select Course
create table if not exists SC
(
    Sno varchar(20) not null comment "学号",
    Cno varchar(20) not null comment "课程号",
    Grade smallint comment "成绩",
    Semester varchar(20) not null comment "学期",
    Teachingclass varchar(20) not null comment "授课班级",
    primary key (Sno, Cno, Semester) comment "主键",
    foreign key (Sno) references S(Sno) on delete cascade on update cascade,
    foreign key (Cno) references C(Cno) on delete cascade on update cascade
) comment "选课" collate = utf8mb4_unicode_ci;
