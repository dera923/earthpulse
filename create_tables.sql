-- EarthPulse プロジェクト用データベーステーブル作成スクリプト

-- 1. 地震データテーブル
CREATE TABLE IF NOT EXISTS earthquake_data (
    id SERIAL PRIMARY KEY,
    longitude DECIMAL(10, 6) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    mag DECIMAL(4, 2),
    place TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(longitude, latitude, timestamp)
);

-- 2. 火災データテーブル（NASA）
CREATE TABLE IF NOT EXISTS fire_data (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    brightness DECIMAL(6, 2),
    scan DECIMAL(6, 2),
    track DECIMAL(6, 2),
    acq_date DATE,
    acq_time TIME,
    satellite VARCHAR(50),
    instrument VARCHAR(50),
    confidence VARCHAR(10),
    version VARCHAR(10),
    bright_t31 DECIMAL(6, 2),
    frp DECIMAL(8, 2),
    daynight VARCHAR(1),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(latitude, longitude, acq_date, acq_time)
);

-- 3. ネットワーク監視データテーブル（Raspberry Pi用）
CREATE TABLE IF NOT EXISTS network_check (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    target VARCHAR(255) NOT NULL,
    ip INET,
    success BOOLEAN NOT NULL,
    rtt_ms DECIMAL(8, 3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. SNS/通信断情報テーブル（将来実装用）
CREATE TABLE IF NOT EXISTS communication_reports (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL, -- 'twitter', 'reddit', 'news', etc.
    content TEXT NOT NULL,
    location_lat DECIMAL(10, 6),
    location_lon DECIMAL(10, 6),
    location_name VARCHAR(255),
    severity_score INTEGER CHECK (severity_score >= 1 AND severity_score <= 10),
    posted_at TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    keywords TEXT[], -- 災害関連キーワード配列
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- インデックス作成（検索性能向上のため）
CREATE INDEX IF NOT EXISTS idx_earthquake_timestamp ON earthquake_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_earthquake_location ON earthquake_data(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_fire_timestamp ON fire_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_fire_location ON fire_data(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_network_timestamp ON network_check(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_network_target ON network_check(target);
CREATE INDEX IF NOT EXISTS idx_comm_timestamp ON communication_reports(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_comm_location ON communication_reports(location_lat, location_lon);

-- テーブル作成完了
SELECT 'データベーステーブル作成完了' AS status; 