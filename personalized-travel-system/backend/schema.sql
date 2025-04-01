-- 个性化旅游推荐系统数据库表结构
-- 包含用户、景点、美食、日记和路径规划等表

-- 删除已存在的表，避免冲突
DROP TABLE IF EXISTS paths;
DROP TABLE IF EXISTS diaries;
DROP TABLE IF EXISTS foods;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS users;

-- 创建用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    avatar VARCHAR(200),
    bio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    travel_preferences JSON,
    food_preferences JSON,
    budget_level INT DEFAULT 3,
    transportation_preference VARCHAR(50),
    accommodation_preference VARCHAR(50),
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建景点表
CREATE TABLE places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address VARCHAR(200),
    city VARCHAR(50),
    province VARCHAR(50),
    country VARCHAR(50),
    opening_hours VARCHAR(200),
    ticket_price FLOAT,
    contact_phone VARCHAR(20),
    website VARCHAR(200),
    place_type VARCHAR(50),
    tags JSON,
    rating FLOAT DEFAULT 0.0,
    review_count INT DEFAULT 0,
    popularity INT DEFAULT 0,
    suitable_seasons JSON,
    recommended_visit_time FLOAT,
    images JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_city (city),
    INDEX idx_province (province),
    INDEX idx_country (country),
    INDEX idx_place_type (place_type),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建美食表
CREATE TABLE foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_level INT DEFAULT 3,
    cuisine_type VARCHAR(50),
    taste_tags JSON,
    signature_dishes JSON,
    restaurant_name VARCHAR(100),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address VARCHAR(200),
    city VARCHAR(50),
    province VARCHAR(50),
    country VARCHAR(50),
    opening_hours VARCHAR(200),
    contact_phone VARCHAR(20),
    website VARCHAR(200),
    rating FLOAT DEFAULT 0.0,
    review_count INT DEFAULT 0,
    average_cost FLOAT,
    suitable_occasions JSON,
    images JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_restaurant_name (restaurant_name),
    INDEX idx_city (city),
    INDEX idx_cuisine_type (cuisine_type),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建旅游日记表
CREATE TABLE diaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    location_name VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    address VARCHAR(200),
    city VARCHAR(50),
    province VARCHAR(50),
    country VARCHAR(50),
    images JSON,
    is_public BOOLEAN DEFAULT TRUE,
    allow_comments BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    user_id INT NOT NULL,
    tags JSON,
    INDEX idx_title (title),
    INDEX idx_created_at (created_at),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建路径规划表
CREATE TABLE paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    total_distance FLOAT DEFAULT 0.0,
    total_time FLOAT DEFAULT 0.0,
    start_point VARCHAR(100),
    end_point VARCHAR(100),
    start_latitude FLOAT NOT NULL,
    start_longitude FLOAT NOT NULL,
    end_latitude FLOAT NOT NULL,
    end_longitude FLOAT NOT NULL,
    path_points JSON,
    transportation_mode VARCHAR(50) DEFAULT 'walking',
    is_optimized BOOLEAN DEFAULT FALSE,
    has_traffic BOOLEAN DEFAULT FALSE,
    avoid_highways BOOLEAN DEFAULT FALSE,
    avoid_tolls BOOLEAN DEFAULT FALSE,
    user_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 添加初始数据

-- 添加管理员用户 (密码哈希值对应 'admin123')
INSERT INTO users (username, email, password_hash, is_admin, created_at)
VALUES ('admin', 'admin@example.com', '$2b$12$rj8MnLcKBxAgL7GUHvYkQOuUUCD0PWwXZ6VB5MoUfuuN0c9V2HUWK', TRUE, CURRENT_TIMESTAMP);

-- 添加测试用户 (密码哈希值对应 'password123')
INSERT INTO users (username, email, password_hash, created_at, travel_preferences, food_preferences, budget_level)
VALUES ('testuser', 'test@example.com', '$2b$12$1oE4MZ1OwHQQiR.hgeOV6.1cQZzD9LK1UNf3XwV.R.Ekb0FvS7ZK.', CURRENT_TIMESTAMP, '["自然风光", "历史文化", "美食体验"]', '["中餐", "日料", "甜点"]', 3);

-- 添加示例景点数据
INSERT INTO places (name, description, latitude, longitude, address, city, province, country, place_type, tags, rating, popularity, images)
VALUES 
('西湖', '杭州市西湖是中国大陆首批国家重点风景名胜区和中国十大风景名胜之一。', 30.2590, 120.1490, '浙江省杭州市西湖区', '杭州', '浙江', '中国', '自然风光', '["湖泊", "文化", "世界遗产"]', 4.8, 100, '["westlake1.jpg", "westlake2.jpg"]'),
('故宫', '北京故宫是中国明清两代的皇家宫殿，旧称紫禁城，是中国古代宫廷建筑之精华。', 39.9163, 116.3972, '北京市东城区景山前街4号', '北京', '北京', '中国', '历史遗迹', '["古迹", "博物馆", "世界遗产"]', 4.9, 95, '["forbidden_city1.jpg", "forbidden_city2.jpg"]');

-- 添加示例美食数据
INSERT INTO foods (name, description, cuisine_type, restaurant_name, latitude, longitude, address, city, province, country, price_level, rating, taste_tags)
VALUES 
('北京烤鸭', '北京烤鸭是具有世界声誉的北京著名菜式，用特殊方法烤制全鸭。', '中餐', '全聚德', 39.9146, 116.4111, '北京市东城区前门大街32号', '北京', '北京', '中国', 4, 4.7, '["咸鲜", "烤制", "经典"]'),
('杭州东坡肉', '东坡肉是浙江杭州名菜，为纪念北宋文学家苏东坡而名。', '中餐', '楼外楼', 30.2461, 120.1450, '浙江省杭州市西湖区孤山路30号', '杭州', '浙江', '中国', 3, 4.5, '["甜咸", "红烧", "传统"]');