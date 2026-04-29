

def get_schema_queries():
    return {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(30) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone_number VARCHAR(11),
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                avatar_url VARCHAR(255),
                city VARCHAR(50),
                bio TEXT,
                is_premium BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                reputation_score INT DEFAULT 0,
                specialty_score INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,

        "password_recovery": """
        CREATE TABLE IF NOT EXISTS password_recovery (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            code VARCHAR(6) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '15 minutes'),
            is_used BOOLEAN DEFAULT FALSE,
            CONSTRAINT fk_user
                FOREIGN KEY(user_id) 
                REFERENCES users(id)
                ON DELETE CASCADE
        );
    """,

        "posts": """
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(120),
                content TEXT NOT NULL,
                post_type VARCHAR(30) DEFAULT 'post',
                image_url VARCHAR(255),
                likes_count INT DEFAULT 0,
                comments_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,

        "comments": """
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,

        "likes": """
            CREATE TABLE IF NOT EXISTS likes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, post_id)
            );
        """,

        "connections": """
            CREATE TABLE IF NOT EXISTS user_connections (
                id SERIAL PRIMARY KEY,
                follower_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                following_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(follower_id, following_id)
            );
        """,

        "skills": """
            CREATE TABLE IF NOT EXISTS skills (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            );
        """,

        "user_skills": """
            CREATE TABLE IF NOT EXISTS user_skills (
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
                level VARCHAR(20) DEFAULT 'beginner',
                PRIMARY KEY (user_id, skill_id)
            );
        """,

        "tags": """
            CREATE TABLE IF NOT EXISTS tags (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            );
        """,

        "post_tags": """
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (post_id, tag_id)
            );
        """,

        "jobs": """
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                company_name VARCHAR(100),
                title VARCHAR(100),
                description TEXT,
                city VARCHAR(50),
                required_skills TEXT[], 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
    }