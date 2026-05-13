

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

        "update_users_v2": """
                   ALTER TABLE users
                       ADD COLUMN IF NOT EXISTS resume_file_url VARCHAR (255),
                       ADD COLUMN IF NOT EXISTS social_links JSONB DEFAULT '{}',
                       ADD COLUMN IF NOT EXISTS specialty VARCHAR(100) 
                   """,

        "user_experiences": """
                            CREATE TABLE IF NOT EXISTS user_experiences
                            ( id SERIAL PRIMARY KEY,
                                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                                company_name VARCHAR(100),
                                job_title VARCHAR(100) NOT NULL,
                                employment_type VARCHAR(50) DEFAULT 'Full-time',
                                start_date DATE,
                                end_date DATE,
                                description TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                );
                            """,

        "user_education": """
                          CREATE TABLE IF NOT EXISTS user_education
                          (
                              id SERIAL PRIMARY KEY,
                              user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                              institution VARCHAR(150) NOT NULL,
                              degree VARCHAR(100),
                              graduation_year INTEGER,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                          """,

        "offerings": """
            CREATE TABLE IF NOT EXISTS offerings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(150) NOT NULL,
                description TEXT,
                price DECIMAL(12, 2) DEFAULT 0.00,
                preview_image_url VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                level VARCHAR(20) DEFAULT 'Intermediate',
                PRIMARY KEY (user_id, skill_id)
            );
        """,

        "update_user_skills_v1": """
            ALTER TABLE user_skills 
            ADD COLUMN IF NOT EXISTS description TEXT
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
<<<<<<< HEAD
        """
    }

=======
        """,

        "user_subscriptions": """
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                user_subscription_id SERIAL PRIMARY KEY,
                plan_id INTEGER REFERENCES subscription_plans(plan_id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                status VARCHAR(20) CHECK (status IN ('active','cancelled','expired')) DEFAULT 'active',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                payment_method VARCHAR(50),
                last_payment_id INTEGER REFERENCES payments(payment_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,

        "unique_subscriptions": """
            CREATE UNIQUE INDEX IF NOT EXISTS unique_active_user_subscription
            ON user_subscriptions(user_id)
            WHERE status = 'active';
        """,

        "update_users_v2": """
               ALTER TABLE users
                   ADD COLUMN IF NOT EXISTS resume_file_url VARCHAR (255),
                   ADD COLUMN IF NOT EXISTS social_links JSONB DEFAULT '{}',
                   ADD COLUMN IF NOT EXISTS specialty VARCHAR(100) -- اینجا کاما گذاشتیم
               """,
    }
>>>>>>> subscription
