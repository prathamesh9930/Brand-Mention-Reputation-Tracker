// 🚀 Netlify Serverless Function for Brand Tracker API
// Handles all FastAPI routes through serverless functions

const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
    try {
        // Set environment variables
        process.env.NEWS_API_KEY = '771f41596a4d4d2ab79a6581c9c01024';
        process.env.ENVIRONMENT = 'production';
        process.env.DEBUG = 'false';
        process.env.FORCE_HTTPS = 'true';

        // Import the FastAPI app
        const { spawn } = require('child_process');
        
        return new Promise((resolve, reject) => {
            const python = spawn('python', ['-c', `
import sys
import os
sys.path.append('${path.join(__dirname, '../../..')}')

from app.main import app
from mangum import Mangum

# Create Mangum adapter for AWS Lambda/Netlify
handler = Mangum(app, lifespan="off")

# Handle the request
import json
event = ${JSON.stringify(event)}
context = ${JSON.stringify(context)}

result = handler(event, context)
print(json.dumps(result))
            `], {
                cwd: path.join(__dirname, '../../..'),
                env: {
                    ...process.env,
                    PYTHONPATH: path.join(__dirname, '../../..')
                }
            });

            let output = '';
            let error = '';

            python.stdout.on('data', (data) => {
                output += data.toString();
            });

            python.stderr.on('data', (data) => {
                error += data.toString();
            });

            python.on('close', (code) => {
                if (code === 0) {
                    try {
                        const result = JSON.parse(output.trim());
                        resolve(result);
                    } catch (e) {
                        resolve({
                            statusCode: 200,
                            body: output
                        });
                    }
                } else {
                    resolve({
                        statusCode: 500,
                        body: JSON.stringify({ 
                            error: 'Internal server error', 
                            details: error 
                        })
                    });
                }
            });
        });

    } catch (error) {
        return {
            statusCode: 500,
            body: JSON.stringify({ 
                error: 'Server error',
                message: error.message 
            })
        };
    }
};