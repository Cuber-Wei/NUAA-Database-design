-- 用户信息视图使用示例

-- 1. 查看所有用户的完整信息
SELECT * FROM user_info_view;

-- 2. 查看特定用户的信息（按用户名查询）
SELECT * FROM user_info_view 
WHERE 用户名 = '特定用户名';

-- 3. 查看抽卡次数最多的前10名用户
SELECT 用户名, 总抽卡次数, 角色抽卡次数, 武器抽卡次数, 最后抽卡时间
FROM user_info_view 
WHERE 总抽卡次数 > 0
ORDER BY 总抽卡次数 DESC 
LIMIT 10;

-- 4. 查看5星收集情况（按五星总数排序）
SELECT 用户名, 五星角色数量, 五星武器数量, 
       (五星角色数量 + 五星武器数量) AS 五星总数,
       总抽卡次数
FROM user_info_view 
WHERE 总抽卡次数 > 0
ORDER BY (五星角色数量 + 五星武器数量) DESC;

-- 5. 查看接近保底的用户（5星保底还剩10次以内）
SELECT 用户名, 角色5星保底剩余, 武器5星保底剩余, 总抽卡次数
FROM user_info_view 
WHERE 角色5星保底剩余 <= 10 OR 武器5星保底剩余 <= 10
ORDER BY LEAST(角色5星保底剩余, 武器5星保底剩余);

-- 6. 查看最近活跃的用户（最近7天有抽卡记录）
SELECT 用户名, 总抽卡次数, 最后抽卡时间
FROM user_info_view 
WHERE 最后抽卡时间 >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY 最后抽卡时间 DESC;

-- 7. 统计用户抽卡行为分析
SELECT 
    COUNT(*) as 用户总数,
    COUNT(CASE WHEN 总抽卡次数 > 0 THEN 1 END) as 有抽卡记录用户数,
    AVG(CASE WHEN 总抽卡次数 > 0 THEN 总抽卡次数 END) as 平均抽卡次数,
    MAX(总抽卡次数) as 最高抽卡次数,
    SUM(五星角色数量) as 全服五星角色总数,
    SUM(五星武器数量) as 全服五星武器总数
FROM user_info_view;

-- 8. 查看用户保底状态分布
SELECT 
    CASE 
        WHEN 角色5星保底剩余 <= 10 THEN '角色即将保底(≤10次)'
        WHEN 角色5星保底剩余 <= 30 THEN '角色接近保底(11-30次)'
        WHEN 角色5星保底剩余 <= 60 THEN '角色中等距离(31-60次)'
        ELSE '角色距离较远(>60次)'
    END as 角色保底状态,
    COUNT(*) as 用户数量
FROM user_info_view 
WHERE 总抽卡次数 > 0
GROUP BY 
    CASE 
        WHEN 角色5星保底剩余 <= 10 THEN '角色即将保底(≤10次)'
        WHEN 角色5星保底剩余 <= 30 THEN '角色接近保底(11-30次)'
        WHEN 角色5星保底剩余 <= 60 THEN '角色中等距离(31-60次)'
        ELSE '角色距离较远(>60次)'
    END;

-- 9. 创建一个更简化的用户摘要视图（可选）
-- CREATE VIEW user_summary_view AS
-- SELECT 
--     用户ID,
--     用户名,
--     总抽卡次数,
--     (五星角色数量 + 五星武器数量) AS 五星总数,
--     LEAST(角色5星保底剩余, 武器5星保底剩余) AS 最近保底距离,
--     最后抽卡时间
-- FROM user_info_view; 