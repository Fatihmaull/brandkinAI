# BrandKin AI - End-to-End Implementation

AI-powered brand identity creation platform built on Alibaba Cloud.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (OSS)                           │
│                   Next.js + React + Tailwind                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                │
│              AppKey + AppSecret Authentication                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              FUNCTION COMPUTE 3.0 (Python 3.10)                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Stage 0 │ │ Stage 1 │ │ Stage 2 │ │ Stage 4 │ │ Stage 5 │  │
│  │  Init   │ │   DNA   │ │ Visual  │ │  Poses  │ │  Code   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│  ┌─────────┐ ┌─────────┐                                       │
│  │ Stage 6 │ │ Stage 7 │                                       │
│  │ Revision│ │Assembly │                                       │
│  └─────────┘ └─────────┘                                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  DashScope   │ │    OSS   │ │  RDS MySQL   │
│ qwen-max     │ │  Assets  │ │  Metadata    │
│ qwen-coder+  │ │  Storage │ │  Tracking    │
│ wanx-v1      │ │          │ │              │
└──────────────┘ └──────────┘ └──────────────┘
```

## Pipeline Stages

| Stage | Name | Description | AI Model |
|-------|------|-------------|----------|
| 0 | Initialize | Create project, store brand brief | - |
| 1 | Brand DNA | Analyze brand brief, extract DNA | qwen-max |
| 2 | Visual Gen | Generate mascot & avatar | wanx-v1 (seed=42) |
| 3 | Selection | User selects character | - |
| 4 | Pose Pack | Generate 5 pose variations | qwen-max + wanx-v1 |
| 5 | Code Export | Generate React component | qwen-coder-plus |
| 6 | Revision | Handle user feedback | qwen-max + wanx-v1 |
| 7 | Assembly | Create brand kit ZIP | qwen-max + wanx-v1 |

## Technical Guardrails

- **100% Alibaba Cloud**: FC, OSS, RDS, MNS, API Gateway, RAM, DashScope
- **Seed Consistency**: All visual generation uses seed=42
- **Security**: STS tokens via environment variables, no hardcoded credentials
- **OSS URLs**: Signed URLs with 24-hour TTL

## Project Structure

```
brandkin-ai/
├── backend/
│   ├── fc-functions/
│   │   ├── orchestrator/
│   │   │   └── api_handler.py
│   │   ├── stage_handlers/
│   │   │   ├── stage0_init.py
│   │   │   ├── stage1_dna.py
│   │   │   ├── stage2_visual.py
│   │   │   ├── stage3_selection.py
│   │   │   ├── stage4_poses.py
│   │   │   ├── stage5_code.py
│   │   │   ├── stage6_revision.py
│   │   │   └── stage7_assembly.py
│   │   └── utils/
│   │       ├── credentials.py
│   │       ├── dashscope_client.py
│   │       ├── database.py
│   │       └── oss_handler.py
│   ├── requirements.txt
│   └── template.yml
├── frontend/
│   ├── nextjs-app/
│   │   ├── app/
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── BrandDNAWizard.tsx
│   │   │   ├── StageTracker.tsx
│   │   │   ├── AssetGallery.tsx
│   │   │   └── CodePreview.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── tailwind.config.ts
│   └── deploy-to-oss.sh
├── infrastructure/
│   └── ram-policies/
│       └── fc-role-policy.json
└── shared/
    └── prompts/
        └── stage_prompts.py
```

## Deployment

### Backend (Function Compute)

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Deploy using Fun (Serverless Devs)
s deploy
```

### Frontend (OSS)

```bash
cd frontend
# Make deploy script executable and run
chmod +x deploy-to-oss.sh
./deploy-to-oss.sh
```

## Environment Variables

### Backend (FC)
- `ALIBABA_CLOUD_ACCESS_KEY_ID` - STS Access Key
- `ALIBABA_CLOUD_ACCESS_KEY_SECRET` - STS Secret
- `ALIBABA_CLOUD_SECURITY_TOKEN` - STS Token
- `DASHSCOPE_API_KEY` - DashScope API Key
- `OSS_BUCKET` - OSS Bucket name
- `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD` - RDS credentials

### Frontend
- `NEXT_PUBLIC_API_BASE_URL` - API Gateway endpoint
- `NEXT_PUBLIC_WEBSOCKET_URL` - WebSocket endpoint
- `NEXT_PUBLIC_APP_KEY` - API Gateway AppKey
- `NEXT_PUBLIC_APP_SECRET` - API Gateway AppSecret

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/projects | Create new project (Stage 0) |
| GET | /api/v1/projects/{id} | Get project status |
| GET | /api/v1/projects/{id}/assets | Get project assets |
| POST | /api/v1/projects/{id}/select | Select character (Stage 3) |
| POST | /api/v1/projects/{id}/revise | Request revision (Stage 6) |
| POST | /api/v1/projects/{id}/finalize | Finalize brand kit (Stage 7) |
| GET | /api/v1/projects/{id}/code | Get code exports |

## License

Copyright 2026 BrandKin AI. All rights reserved.
