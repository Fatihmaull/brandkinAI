-- BrandKin AI - MySQL Database Schema
-- Run this in phpMyAdmin to set up your local database

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS brandkin_ai_local 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE brandkin_ai_local;

-- Projects table: Stores all brand projects
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(64) PRIMARY KEY,
    brand_brief JSON NOT NULL,
    status VARCHAR(32) DEFAULT 'initialized',
    current_stage INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    error_message TEXT,
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Assets table: Stores mascots, avatars, poses, and other visual assets
CREATE TABLE IF NOT EXISTS assets (
    asset_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    asset_type ENUM('mascot', 'avatar', 'pose', 'banner', 'logo', 'icon') NOT NULL,
    stage INT NOT NULL,
    oss_url VARCHAR(512),
    transparent_url VARCHAR(512),
    metadata JSON,
    is_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_type (asset_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Generations tracking table: Tracks AI generation jobs
CREATE TABLE IF NOT EXISTS generations (
    generation_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    stage INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    input_params JSON,
    output_result JSON,
    error_message TEXT,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project_stage (project_id, stage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Code exports table: Stores generated React components
CREATE TABLE IF NOT EXISTS code_exports (
    export_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    component_name VARCHAR(128),
    react_code TEXT,
    css_keyframes TEXT,
    usage_snippet TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Brand kits table: Stores assembled brand kit downloads
CREATE TABLE IF NOT EXISTS brand_kits (
    kit_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    zip_url VARCHAR(512),
    signed_url VARCHAR(512),
    url_expires_at TIMESTAMP NULL,
    download_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Brand DNA cache table: Stores extracted brand DNA for quick access
CREATE TABLE IF NOT EXISTS brand_dna (
    dna_id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    brand_name VARCHAR(256),
    brand_personality JSON,
    target_audience JSON,
    visual_style JSON,
    mascot_concept JSON,
    avatar_concept JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- View: Project summary with asset counts
-- Note: JSON_EXTRACT is used for MariaDB compatibility
CREATE OR REPLACE VIEW project_summary AS
SELECT 
    p.project_id,
    JSON_UNQUOTE(JSON_EXTRACT(p.brand_brief, '$.brand_name')) as brand_name,
    p.status,
    p.current_stage,
    p.created_at,
    p.updated_at,
    COUNT(DISTINCT a.asset_id) as total_assets,
    COUNT(DISTINCT CASE WHEN a.asset_type = 'mascot' THEN a.asset_id END) as mascot_count,
    COUNT(DISTINCT CASE WHEN a.asset_type = 'avatar' THEN a.asset_id END) as avatar_count,
    COUNT(DISTINCT CASE WHEN a.asset_type = 'pose' THEN a.asset_id END) as pose_count,
    COUNT(DISTINCT CASE WHEN a.is_selected = TRUE THEN a.asset_id END) as selected_count,
    COUNT(DISTINCT ce.export_id) as code_exports_count
FROM projects p
LEFT JOIN assets a ON p.project_id = a.project_id
LEFT JOIN code_exports ce ON p.project_id = ce.project_id
GROUP BY p.project_id;

-- Insert sample data for testing (optional)
-- Uncomment below to add a test project

/*
INSERT INTO projects (project_id, brand_brief, status, current_stage) VALUES
('test-project-001', 
 '{"brand_name": "Test Brand", "brand_personality": ["innovative", "friendly"], "brand_story": "A test brand for development"}',
 'completed', 7);

INSERT INTO assets (asset_id, project_id, asset_type, stage, oss_url, is_selected) VALUES
('asset-001', 'test-project-001', 'mascot', 2, 'https://example.com/mascot.png', TRUE),
('asset-002', 'test-project-001', 'avatar', 2, 'https://example.com/avatar.png', FALSE),
('asset-003', 'test-project-001', 'pose', 4, 'https://example.com/pose1.png', FALSE),
('asset-004', 'test-project-001', 'pose', 4, 'https://example.com/pose2.png', FALSE);
*/
