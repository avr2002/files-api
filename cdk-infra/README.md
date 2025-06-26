# Files API CDK Stack

1. S3 bucket for storing files
2. Lambda Function for our FastAPI app with Lambda Layer
3. Lambda function should have access to the S3 bucket
4. API Gateway to expose the Lambda function as REST API
5. Cloudwatch for logging and monitoring
6. Enable X-Ray, metrics, and tracing
