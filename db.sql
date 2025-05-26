create database if not exists wishes_db;

use wishes_db;

-- Table1: Characters
create table if not exists characters
(
    Cno bigint primary key comment "角色号",
    Cname varchar(20) not null comment "角色名", 
    Grade smallint not null comment "等级",
    index idx_cname (Cname),
    index idx_grade (Grade)
) comment "角色" collate = utf8mb4_unicode_ci;

-- Table2: Weapons
create table if not exists weapons
(
    Wno bigint primary key comment "武器号",
    Wname varchar(20) not null comment "武器名",
    Grade smallint not null comment "等级",
    index idx_wname (Wname),
    index idx_grade (Grade)
) comment "武器" collate = utf8mb4_unicode_ci;

-- Table3: Users
create table if not exists users
(
    Uno bigint primary key comment "用户号",
    Uname varchar(20) not null comment "用户名",
    Upassword varchar(64) not null comment "密码（md5）",
    character_4star_pity int default 0 comment "角色卡池4星保底计数",
    weapon_4star_pity int default 0 comment "武器卡池4星保底计数",
    character_5star_pity int default 0 comment "角色卡池5星保底计数",
    weapon_5star_pity int default 0 comment "武器卡池5星保底计数",
    index idx_uname (Uname)
) comment "用户" collate = utf8mb4_unicode_ci;

-- Table4: Wishes
create table if not exists wishes
(
    Wno bigint primary key comment "抽卡记录ID",
    Wuser bigint not null comment "抽卡记录用户ID",
    Wtype tinyint not null comment "抽卡记录类型（0：角色，1：武器）",
    Wcharacter bigint null comment "抽卡记录角色ID",
    Wweapon bigint null comment "抽卡记录武器ID",
    Wtime datetime not null comment "抽卡记录时间",
    index idx_wuser (Wuser),
    index idx_wtype (Wtype),
    index idx_wcharacter (Wcharacter),
    index idx_wwapon (Wweapon),
    foreign key (Wuser) references users(Uno) on delete cascade on update cascade,
    foreign key (Wcharacter) references characters(Cno) on delete cascade on update cascade,
    foreign key (Wweapon) references weapons(Wno) on delete cascade on update cascade
) comment "抽卡记录" collate = utf8mb4_unicode_ci;
