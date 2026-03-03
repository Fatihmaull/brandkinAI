# BrandKin AI

AI-powered brand identity creation platform built on Alibaba Cloud services.

## Architecture

- **Backend**: Alibaba Cloud Function Compute 3.0 (Python 3.10)
- **Frontend**: Next.js (static export) on Alibaba Cloud OSS
- **Database**: RDS MySQL
- **Storage**: OSS with signed URLs
- **AI Models**: Model Studio (qwen-max, qwen-coder-plus, wanx-v1)

## Pipeline Stages

| Stage | Name | AI Model | Description |
|-------|------|----------|-------------|
| 0 | Initialize | — | Create project |
| 1 | Brand DNA | qwen-max | Analyze brand brief |
| 2 | Visual Gen | wanx-v1 | Generate mascot/avatar (seed=42) |
| 3 | Selection | — | User selects character |
| 4 | Pose Pack | wanx-v1 | Generate 5 pose variations |
| 5 | Code Export | qwen-coder-plus | Generate React components |
| 6 | Revision | qwen-max + wanx-v1 | Handle user feedback |
| 7 | Assembly | qwen-max + wanx-v1 | Create brand kit ZIP |

## Project Structure

```
brandkin-ai/
├── backend/
│   ├── fc-functions/           # Function Compute code
│   │   ├── orchestrator/       # API handler (routing)
│   │   ├── stage_handlers/     # Stage 0-7 handlers
│   │   ├── utils/              # AI client, DB, OSS, credentials
│   │   └── prompts/            # AI prompt templates
│   ├── database/               # SQL schema
│   ├── requirements.txt        # Python dependencies
│   └── template.yml            # FC deployment template
├── frontend/
│   ├── nextjs-app/             # Next.js application
│   └── deploy-to-oss.sh        # Frontend deployment script
├── infrastructure/
│   └── ram-policies/           # IAM policies
└── .env.example                # Environment variable template
```

## Setup

### Prerequisites

- Alibaba Cloud account with:
  - Function Compute 3.0
  - RDS MySQL instance
  - OSS bucket
  - Model Studio API key (DashScope International)
- Node.js 18+ (frontend)
- Python 3.10+ (backend)
- [Serverless Devs CLI](https://www.serverless-devs.com/) (`s` command)
- [ossutil](https://www.alibabacloud.com/help/doc-detail/120075.htm)

### Environment Variables

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

Key variables:
- `MODELSTUDIO_API_KEY` — Model Studio API key (required)
- `OSS_BUCKET` / `OSS_ENDPOINT` — OSS configuration
- `RDS_HOST` / `RDS_PASSWORD` — Database credentials
- `MNS_ENDPOINT` — Message queue endpoint

### Database Setup

Run the schema on your RDS instance:

```bash
mysql -h <RDS_HOST> -u brandkin_admin -p brandkin_ai < backend/database/init_schema.sql
```

### Backend Deployment

```bash
cd backend
pip install -r requirements.txt
s deploy  # Deploy to FC using template.yml
```

### Frontend Deployment

```bash
cd frontend
OSS_BUCKET=your-bucket OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com ./deploy-to-oss.sh
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Get project status |
| GET | `/api/v1/projects/{id}/assets` | Get assets |
| GET | `/api/v1/projects/{id}/code` | Get code exports |
| POST | `/api/v1/projects/{id}/select` | Select character |
| POST | `/api/v1/projects/{id}/revise` | Request revision |
| POST | `/api/v1/projects/{id}/finalize` | Generate brand kit |

## Technical Guardrails

- **Seed 42**: All image generation uses seed=42 for mascot/avatar consistency
- **Signed URLs**: OSS URLs expire after 24 hours
- **STS Auth**: FC uses RAM role for secure credential injection
- **No client-side secrets**: API Gateway authentication is server-side
