// 🚀 Netlify Serverless Function for Brand Tracker API
// Handles all FastAPI routes through serverless functions

exports.handler = async (event, context) => {
    try {
        // Set environment variables
        process.env.NEWS_API_KEY = '771f41596a4d4d2ab79a6581c9c01024';
        process.env.ENVIRONMENT = 'production';
        process.env.DEBUG = 'false';
        process.env.FORCE_HTTPS = 'true';
        process.env.DATABASE_URL = 'sqlite:///./brand_tracker.db';
        
        // Simple response for testing
        const path = event.path.replace('/.netlify/functions/api', '');
        const method = event.httpMethod;
        
        console.log('API Request:', { method, path, body: event.body });
        
        // Handle CORS preflight
        if (method === 'OPTIONS') {
            return {
                statusCode: 200,
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                body: JSON.stringify({ message: 'OK' })
            };
        }
        
        // Handle health check
        if (path === '/api/health' || path === '/health') {
            return {
                statusCode: 200,
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    status: 'healthy',
                    timestamp: new Date().toISOString(),
                    environment: 'netlify-functions'
                })
            };
        }
        
        // Handle brands endpoints
        if (path === '/api/brands/' && method === 'GET') {
            return {
                statusCode: 200,
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data: [
                        {
                            id: 1,
                            name: "Demo Brand",
                            keywords: ["demo", "test"],
                            created_at: new Date().toISOString(),
                            is_active: true,
                            alert_threshold: 10,
                            sentiment_threshold: -0.5
                        }
                    ]
                })
            };
        }
        
        if (path === '/api/brands/add' && method === 'POST') {
            const body = JSON.parse(event.body || '{}');
            return {
                statusCode: 200,
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data: {
                        id: Date.now(),
                        name: body.name,
                        keywords: body.keywords || [],
                        created_at: new Date().toISOString(),
                        is_active: true,
                        alert_threshold: body.alert_threshold || 10,
                        sentiment_threshold: body.sentiment_threshold || -0.5
                    }
                })
            };
        }
        
        // Default response for unhandled routes
        return {
            statusCode: 404,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                error: 'Not Found',
                path,
                method,
                message: 'API endpoint not implemented yet'
            })
        };
        
    } catch (error) {
        console.error('API Error:', error);
        return {
            statusCode: 500,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                error: 'Internal server error',
                message: error.message 
            })
        };
    }
};