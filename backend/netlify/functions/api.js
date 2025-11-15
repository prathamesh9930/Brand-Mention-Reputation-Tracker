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
        
        console.log('=== API REQUEST DEBUG ===');
        console.log('Original event.path:', event.path);
        console.log('Cleaned path:', path);
        console.log('Method:', method);
        console.log('Body:', event.body);
        console.log('========================');
        
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
        
        // Handle brands endpoints - support both with and without trailing slash
        if ((path === '/brands/' || path === '/brands' || path === '/api/brands' || path === '/api/brands/') && method === 'GET') {
            console.log('✅ Brands GET endpoint matched!');
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
        
        // Handle add brand endpoint
        if ((path === '/brands/add' || path === '/api/brands/add') && method === 'POST') {
            console.log('✅ Brands POST endpoint matched!');
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
        console.log('❌ No route matched. Available routes:');
        console.log('GET /brands, /brands/, /api/brands, /api/brands/');
        console.log('POST /brands/add, /api/brands/add');
        console.log('GET /health, /api/health');
        
        return {
            statusCode: 404,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                error: 'Not Found',
                path: path,
                originalPath: event.path,
                method: method,
                message: 'API endpoint not found. Check logs for debugging.',
                availableRoutes: [
                    'GET /brands',
                    'POST /brands/add',
                    'GET /health'
                ]
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