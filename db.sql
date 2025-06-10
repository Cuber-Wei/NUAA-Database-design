create database if not exists wishes_db;

use wishes_db;

-- Table1: Characters
create table if not exists characters
(
    Cno     bigint      primary key comment "角色号",
    Cname   varchar(20) not null    comment "角色名", 
    Grade   smallint    not null    comment "等级",
    index idx_cname (Cname),
    index idx_grade (Grade)
) comment "角色" collate = utf8mb4_unicode_ci;

-- Table2: Weapons
create table if not exists weapons
(
    Wno     bigint      primary key comment "武器号",
    Wname   varchar(20) not null    comment "武器名",
    Grade   smallint    not null    comment "等级",
    index idx_wname (Wname),
    index idx_grade (Grade)
) comment "武器" collate = utf8mb4_unicode_ci;

-- Table3: Users
create table if not exists users
(
    Uno                     bigint          primary key comment "用户号",
    Uname                   varchar(20)     not null    comment "用户名",
    Upassword               varchar(64)     not null    comment "密码（md5）",
    character_4star_pity    int default 0               comment "角色卡池4星保底计数",
    weapon_4star_pity       int default 0               comment "武器卡池4星保底计数",
    character_5star_pity    int default 0               comment "角色卡池5星保底计数",
    weapon_5star_pity       int default 0               comment "武器卡池5星保底计数",
    index idx_uname (Uname)
) comment "用户" collate = utf8mb4_unicode_ci;

-- Table4: Wishes
create table if not exists wishes
(
    Wno         bigint   primary key comment "抽卡记录ID",
    Wuser       bigint   not null    comment "抽卡记录用户ID",
    Wtype       tinyint  not null    comment "抽卡记录类型（0：角色，1：武器）",
    Wcharacter  bigint   null        comment "抽卡记录角色ID",
    Wweapon     bigint   null        comment "抽卡记录武器ID",
    Wtime       datetime not null    comment "抽卡记录时间",
    index idx_wuser (Wuser),
    index idx_wtype (Wtype),
    index idx_wcharacter (Wcharacter),
    index idx_wwapon (Wweapon),
    foreign key (Wuser)      references users(Uno)      on delete cascade on update cascade,
    foreign key (Wcharacter) references characters(Cno) on delete cascade on update cascade,
    foreign key (Wweapon)    references weapons(Wno)    on delete cascade on update cascade
) comment "抽卡记录" collate = utf8mb4_unicode_ci;

-- 视图：用户信息展示视图
CREATE VIEW user_info_view AS
SELECT 
    u.Uno AS 用户ID,
    u.Uname AS 用户名,
    u.character_4star_pity AS 角色4星保底计数,
    u.weapon_4star_pity AS 武器4星保底计数,
    u.character_5star_pity AS 角色5星保底计数,
    u.weapon_5star_pity AS 武器5星保底计数,
    -- 计算保底剩余次数
    (10 - u.character_4star_pity) AS 角色4星保底剩余,
    (10 - u.weapon_4star_pity) AS 武器4星保底剩余,
    (80 - u.character_5star_pity) AS 角色5星保底剩余,
    (80 - u.weapon_5star_pity) AS 武器5星保底剩余,
    -- 统计抽卡总数
    COALESCE(wish_stats.total_wishes, 0) AS 总抽卡次数,
    COALESCE(wish_stats.character_wishes, 0) AS 角色抽卡次数,
    COALESCE(wish_stats.weapon_wishes, 0) AS 武器抽卡次数,
    -- 统计5星角色和武器数量
    COALESCE(char_5star.count_5star, 0) AS 五星角色数量,
    COALESCE(weapon_5star.count_5star, 0) AS 五星武器数量,
    -- 最后抽卡时间
    wish_stats.last_wish_time AS 最后抽卡时间
FROM users u
LEFT JOIN (
    -- 抽卡统计子查询
    SELECT 
        w.Wuser,
        COUNT(*) as total_wishes,
        SUM(CASE WHEN w.Wtype = 0 THEN 1 ELSE 0 END) as character_wishes,
        SUM(CASE WHEN w.Wtype = 1 THEN 1 ELSE 0 END) as weapon_wishes,
        MAX(w.Wtime) as last_wish_time
    FROM wishes w
    GROUP BY w.Wuser
) wish_stats ON u.Uno = wish_stats.Wuser
LEFT JOIN (
    -- 5星角色统计
    SELECT 
        w.Wuser,
        COUNT(*) as count_5star
    FROM wishes w 
    JOIN characters c ON w.Wcharacter = c.Cno
    WHERE w.Wtype = 0 AND c.Grade = 5
    GROUP BY w.Wuser
) char_5star ON u.Uno = char_5star.Wuser
LEFT JOIN (
    -- 5星武器统计
    SELECT 
        w.Wuser,
        COUNT(*) as count_5star
    FROM wishes w 
    JOIN weapons wp ON w.Wweapon = wp.Wno
    WHERE w.Wtype = 1 AND wp.Grade = 5
    GROUP BY w.Wuser
) weapon_5star ON u.Uno = weapon_5star.Wuser
COMMENT '用户信息展示视图';
