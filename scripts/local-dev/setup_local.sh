#!/bin/bash
# scripts/local-dev/setup_local.sh: Setup local development environment for JIT RAG

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting local development setup...${NC}"

# 1. Backend Setup
echo -e "${GREEN}📦 Setting up Backend (app)...${NC}"
cd app
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${BLUE}✅ Virtual environment created.${NC}"
fi
source .venv/bin/activate
pip install -r requirements.txt
cd ..

# 2. Frontend Setup
echo -e "${GREEN}📦 Setting up Frontend (frontend)...${NC}"
cd frontend
npm install

# 3. Configure Vite Proxy
echo -e "${GREEN}⚙️ Configuring Vite proxy...${NC}"
cat <<EOF > vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      }
    }
  }
})
EOF
cd ..

echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. In one terminal, start the backend:"
echo -e "   cd app && source .venv/bin/activate"
echo -e "   export GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>"
echo -e "   python3 -m app.main"
echo -e ""
echo -e "2. In another terminal, start the frontend:"
echo -e "   cd frontend && npm run dev"
