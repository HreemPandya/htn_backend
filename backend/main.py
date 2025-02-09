from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from backend.routes import router  

app = FastAPI(title="Hack The North Backend")


app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Hack The North Backend",
        version="1.0.0",
        description="📌 Secure API with JWT authentication & Role-Based Access Control",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Hack The North API Docs",
        swagger_favicon_url="https://your-logo-url.com/favicon.ico",  # 🔥 Replace with your favicon
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-themes@latest/themes/3.x/theme-monokai.css"  # 🔥 Custom Material Theme
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hack The North API</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary: #2563eb;
                --secondary: #3b82f6;
                --accent: #60a5fa;
                --background: #0f172a;
                --text: #f8fafc;
                --card-bg: #1e293b;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: system-ui, -apple-system, sans-serif;
                background: var(--background);
                color: var(--text);
                line-height: 1.6;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }

            .hero {
                text-align: center;
                padding: 4rem 2rem;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                border-radius: 1rem;
                margin-bottom: 3rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }

            .hero h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                background: linear-gradient(to right, #fff, #e0e7ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero p {
                font-size: 1.25rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }

            .tech-stack {
                background: var(--card-bg);
                padding: 2rem;
                border-radius: 1rem;
                margin-bottom: 3rem;
            }

            .tech-stack h2 {
                color: var(--accent);
                margin-bottom: 1.5rem;
            }

            .tech-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
            }

            .tech-item {
                background: rgba(0, 0, 0, 0.2);
                padding: 1rem;
                border-radius: 0.5rem;
                text-align: center;
            }

            .btn {
                display: inline-block;
                padding: 1rem 2rem;
                background: var(--text);
                color: var(--primary);
                text-decoration: none;
                border-radius: 0.5rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }

            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
            }

            .feature-card {
                background: var(--card-bg);
                padding: 2rem;
                border-radius: 1rem;
                transition: transform 0.3s ease;
            }

            .feature-card:hover {
                transform: translateY(-5px);
            }

            .feature-icon {
                font-size: 2rem;
                color: var(--accent);
                margin-bottom: 1rem;
            }

            .feature-title {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: var(--accent);
            }

            .endpoint-desc {
                color: #94a3b8;
                font-size: 0.85rem;
                margin-left: 1rem;
                margin-bottom: 1rem;
                font-style: italic;
            }

            .method-tag {
                display: inline-block;
                width: 60px;
                text-align: center;
                padding: 0.2rem 0.5rem;
                border-radius: 0.25rem;
                font-size: 0.85rem;
                font-weight: bold;
            }

            .get {
                background: #0d9488;
                color: white;
            }

            .post {
                background: #0891b2;
                color: white;
            }

            .put {
                background: #9333ea;
                color: white;
            }

            .delete {
                background: #dc2626;
                color: white;
            }

            .endpoint {
                background: rgba(0, 0, 0, 0.2);
                padding: 0.75rem;
                border-radius: 0.25rem;
                margin: 0.75rem 0;
                font-family: monospace;
            }


            .endpoint-group {
                margin-bottom: 1.5rem;
            }

            .admin-badge {
                background: #ef4444;
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 0.25rem;
                font-size: 0.8rem;
                margin-left: 0.5rem;
            }

            @media (max-width: 768px) {
                .hero h1 {
                    font-size: 2rem;
                }
                
                .features {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>🚀 Hack The North API</h1>
                <p>Build amazing hacker experiences with our comprehensive API suite</p>
                <a href="/docs" class="btn">Explore API Documentation →</a>
            </div>

            <div class="tech-stack">
                <h2>🛠 Tech Stack</h2>
                <div class="tech-grid">
                    <div class="tech-item">
                        <i class="fas fa-server"></i>
                        <h3>FastAPI</h3>
                        <p>Modern Python web framework</p>
                    </div>
                    <div class="tech-item">
                        <i class="fas fa-database"></i>
                        <h3>PostgreSQL</h3>
                        <p>Via Docker container</p>
                    </div>
                    <div class="tech-item">
                        <i class="fas fa-key"></i>
                        <h3>JWT Auth</h3>
                        <p>OAuth2 with Bearer tokens</p>
                    </div>
                    <div class="tech-item">
                        <i class="fas fa-code"></i>
                        <h3>SQLAlchemy</h3>
                        <p>Async ORM integration</p>
                    </div>
                </div>
            </div>

            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-users"></i></div>
                    <h2 class="feature-title">User Management</h2>
                    <div class="endpoint-group">
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /users
                            <div class="endpoint-desc">Retrieve a paginated list of all registered users</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /users/{id}
                            <div class="endpoint-desc">Get detailed information for a specific user</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /users
                            <div class="endpoint-desc">Register a new user with name, email, and role</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag put">PUT</span> /users/{id}
                            <div class="endpoint-desc">Update user profile and preferences</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag delete">DELETE</span> /users/{id} <span class="admin-badge">ADMIN</span>
                            <div class="endpoint-desc">Remove a user from the system (admin only)</div>
                        </div>
                    </div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-key"></i></div>
                    <h2 class="feature-title">Authentication</h2>
                    <div class="endpoint-group">
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /login
                            <div class="endpoint-desc">Authenticate and receive JWT access token</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /protected
                            <div class="endpoint-desc">Test endpoint for validating JWT token</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag put">PUT</span> /promote-admin/{id} <span class="admin-badge">ADMIN</span>
                            <div class="endpoint-desc">Grant admin privileges to a user</div>
                        </div>
                    </div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-chart-bar"></i></div>
                    <h2 class="feature-title">Scans & Analytics</h2>
                    <div class="endpoint-group">
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /scans/{user_id}
                            <div class="endpoint-desc">Record a new scan for event participation</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /scans
                            <div class="endpoint-desc">View all scans with optional date filtering</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /users/{id}/scans
                            <div class="endpoint-desc">Get complete scan history for a user</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /leaderboard
                            <div class="endpoint-desc">View top 10 most active participants</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /popular-activities
                            <div class="endpoint-desc">See trending events and activities</div>
                        </div>
                    </div>
                </div>

                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-ticket-alt"></i></div>
                    <h2 class="feature-title">Event Management</h2>
                    <div class="endpoint-group">
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /check-in
                            <div class="endpoint-desc">Record user arrival at an event</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /check-out
                            <div class="endpoint-desc">Log user departure from an event</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /connect/{id1}/{id2}
                            <div class="endpoint-desc">Create connection between two participants</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag get">GET</span> /random-winner
                            <div class="endpoint-desc">Select random winner from active participants</div>
                        </div>
                        <div class="endpoint">
                            <span class="method-tag post">POST</span> /snacks/{user_id}
                            <div class="endpoint-desc">Register midnight snack claim for user</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
