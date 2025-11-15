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
        
        // Parse the request path and method
        const fullPath = event.path || '';
        const method = event.httpMethod || 'GET';
        
        // Extract the API path by removing the function path
        let apiPath = fullPath.replace('/.netlify/functions/api', '');
        if (!apiPath.startsWith('/')) {
            apiPath = '/' + apiPath;
        }
        
        console.log('=== NETLIFY FUNCTION DEBUG ===');
        console.log('Full Path:', fullPath);
        console.log('API Path:', apiPath);
        console.log('Method:', method);
        console.log('Body:', event.body);
        console.log('Headers:', event.headers);
        console.log('================================');
        
        // CORS headers for all responses
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Content-Type': 'application/json'
        };
        
        // Handle CORS preflight
        if (method === 'OPTIONS') {
            return {
                statusCode: 200,
                headers: corsHeaders,
                body: JSON.stringify({ message: 'CORS OK' })
            };
        }
        
        // Health check endpoint
        if (apiPath === '/health' || apiPath === '/') {
            return {
                statusCode: 200,
                headers: corsHeaders,
                body: JSON.stringify({ 
                    status: 'healthy',
                    timestamp: new Date().toISOString(),
                    environment: 'netlify-functions',
                    path: apiPath
                })
            };
        }
        
        // Get brands endpoint
        if ((apiPath === '/brands' || apiPath === '/brands/') && method === 'GET') {
            return {
                statusCode: 200,
                headers: corsHeaders,
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
        
        // Add brand endpoint
        if (apiPath === '/brands/add' && method === 'POST') {
            try {
                const requestBody = JSON.parse(event.body || '{}');
                return {
                    statusCode: 200,
                    headers: corsHeaders,
                    body: JSON.stringify({
                        data: {
                            id: Date.now(),
                            name: requestBody.name,
                            keywords: requestBody.keywords || [],
                            created_at: new Date().toISOString(),
                            is_active: true,
                            alert_threshold: requestBody.alert_threshold || 10,
                            sentiment_threshold: requestBody.sentiment_threshold || -0.5
                        }
                    })
                };
            } catch (parseError) {
                return {
                    statusCode: 400,
                    headers: corsHeaders,
                    body: JSON.stringify({
                        error: 'Invalid JSON body',
                        details: parseError.message
                    })
                };
            }
        }
        
        // Default 404 response
        return {
            statusCode: 404,
            headers: corsHeaders,
            body: JSON.stringify({
                error: 'Not Found',
                message: `API endpoint not found: ${method} ${apiPath}`,
                availableEndpoints: [
                    'GET /health',
                    'GET /brands',
                    'POST /brands/add'
                ],
                debugInfo: {
                    fullPath: fullPath,
                    apiPath: apiPath,
                    method: method
                }
            })
        };
        
    } catch (error) {
        console.error('Function Error:', error);
        return {
            statusCode: 500,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                error: 'Internal server error',
                message: error.message,
                stack: error.stack
            })
        };
    }
};