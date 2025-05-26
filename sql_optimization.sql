-- SQL性能优化脚本 - 专注于wishes表优化
-- 针对100万级数据量的性能优化方案

USE wishes_db;

-- ========================================
-- 1. 索引优化 - wishes表
-- ========================================

-- 删除现有的单列索引（保留主键和外键约束需要的索引）
ALTER TABLE wishes DROP INDEX IF EXISTS idx_wuser;
ALTER TABLE wishes DROP INDEX IF EXISTS idx_wtype;

-- 添加复合索引以优化常用查询
-- 1. 用户+时间复合索引（用于仪表板和历史记录查询）
ALTER TABLE wishes ADD INDEX idx_user_time_desc (Wuser, Wtime DESC);

-- 2. 用户+类型+时间复合索引（用于按类型筛选的查询）
ALTER TABLE wishes ADD INDEX idx_user_type_time (Wuser, Wtype, Wtime DESC);

-- 3. 覆盖索引（包含常用查询的所有字段，避免回表查询）
ALTER TABLE wishes ADD INDEX idx_user_cover (Wuser, Wtime DESC, Wtype, Wcharacter, Wweapon);

-- 4. 时间索引（用于全局时间排序）
ALTER TABLE wishes ADD INDEX idx_time_desc (Wtime DESC);

-- ========================================
-- 2. 查询优化建议
-- ========================================

-- 原始查询（性能较差）：
-- SELECT w.Wtime, w.Wtype, c.Cname, c.Grade as CGrade, wp.Wname, wp.Grade as WGrade
-- FROM wishes w
-- LEFT JOIN characters c ON w.Wcharacter = c.Cno
-- LEFT JOIN weapons wp ON w.Wweapon = wp.Wno
-- WHERE w.Wuser = %s
-- ORDER BY w.Wtime DESC
-- LIMIT %s OFFSET %s

-- 优化后的查询（使用覆盖索引）：
-- 第一步：获取wishes记录（使用覆盖索引，无需JOIN）
-- SELECT Wtime, Wtype, Wcharacter, Wweapon
-- FROM wishes 
-- WHERE Wuser = %s
-- ORDER BY Wtime DESC
-- LIMIT %s OFFSET %s

-- 第二步：在应用层根据需要查询角色/武器详情

-- ========================================
-- 3. 分页优化方案
-- ========================================

-- 原始分页查询（深度分页性能差）：
-- LIMIT %s OFFSET %s

-- 优化方案：基于游标的分页
-- 首次查询：
-- SELECT Wtime, Wtype, Wcharacter, Wweapon
-- FROM wishes 
-- WHERE Wuser = %s
-- ORDER BY Wtime DESC
-- LIMIT %s

-- 后续分页：
-- SELECT Wtime, Wtype, Wcharacter, Wweapon
-- FROM wishes 
-- WHERE Wuser = %s AND Wtime < %s
-- ORDER BY Wtime DESC
-- LIMIT %s

-- ========================================
-- 4. 统计查询优化
-- ========================================

-- 原始统计查询：
-- SELECT COUNT(*) as total FROM wishes WHERE Wuser = %s

-- 优化方案：使用索引优化的COUNT查询
-- 由于有了 idx_user_time_desc 索引，COUNT查询会更快

-- ========================================
-- 5. 验证索引效果
-- ========================================

-- 查看表的索引信息
-- SHOW INDEX FROM wishes;

-- 分析查询执行计划
-- EXPLAIN SELECT w.Wtime, w.Wtype, w.Wcharacter, w.Wweapon
-- FROM wishes w
-- WHERE w.Wuser = 1
-- ORDER BY w.Wtime DESC
-- LIMIT 10;

-- ========================================
-- 6. 性能监控查询
-- ========================================

-- 查看表状态
-- SHOW TABLE STATUS LIKE 'wishes';

-- 查看索引使用情况
-- SHOW STATUS LIKE 'Handler_read%';

-- 重置统计信息
-- FLUSH STATUS; 