#!/bin/bash
# BrandKin AI - Frontend Deployment Script
# Deploys Next.js static build to Alibaba Cloud OSS

set -e

echo "=== BrandKin AI Frontend Deployment ==="

# Configuration
OSS_BUCKET="brandkin-ai-frontend"
OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
BUILD_DIR="nextjs-app/dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if ossutil is installed
if ! command -v ossutil &> /dev/null; then
    echo -e "${RED}Error: ossutil is not installed${NC}"
    echo "Please install ossutil: https://www.alibabacloud.com/help/doc-detail/120075.htm"
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
cd nextjs-app
npm install

# Build the project
echo -e "${YELLOW}Building Next.js project...${NC}"
npm run build

cd ..

# Sync to OSS
echo -e "${YELLOW}Deploying to OSS...${NC}"
ossutil cp -r -f "$BUILD_DIR/" "oss://$OSS_BUCKET/"

# Set cache headers for static assets
echo -e "${YELLOW}Setting cache headers...${NC}"
ossutil set-meta "oss://$OSS_BUCKET/_next/static/" "Cache-Control:public,max-age=31536000,immutable" --update -r
ossutil set-meta "oss://$OSS_BUCKET/" "Content-Type:text/html" --include "*.html" --update -r

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Your site is available at: https://$OSS_BUCKET.$OSS_ENDPOINT/${NC}"
