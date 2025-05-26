alter table SC
    modify column Grade smallint default null comment '成绩',
    modify column Semester varchar(20) not null comment '开课学期',
    modify column Teachingclass VARCHAR(20) NOT NULL COMMENT '教学班';

alter table C
    modify column Cpno varchar(20) default null comment '先行课',
    rename column Ccredict to Ccredit;

