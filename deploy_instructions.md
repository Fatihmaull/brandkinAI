# Deployment Guide - BrandKin AI

Follow these steps to deploy your application to production (Alibaba Cloud & Vercel).

## 1. Backend Deployment (Alibaba Cloud)

The backend is built with Function Compute 3.0.

### Prerequisites
- Install [Serverless Devs](https://docs.serverless-devs.com/en/user-guide/installing-serverless-devs/): `npm install -g @serverless-devs/s`
- Configure Alibaba Cloud credentials: `s config add`

### Steps
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Update your credentials if needed:
   - Edit `update_credentials.py` with any new keys.
   - Run: `python update_credentials.py`
3. Deploy to Function Compute:
   ```bash
   s deploy -y
   ```

   > [!TIP]
   > The `s.yaml` uses variables like `${env.MODELSTUDIO_API_KEY}`. Ensure these are set in your terminal's environment before deploying, or use a plugin to load them from `.env`.

---

## 2. Frontend Deployment (Vercel)

The frontend is a Next.js application.

### Prerequisites
- [Vercel CLI](https://vercel.com/docs/cli) (optional, or use the Vercel Dashboard).

### Steps
1. Navigate to the frontend directory:
   ```bash
   cd frontend/nextjs-app
   ```
2. Link to Vercel and deploy:
   ```bash
   vercel
   ```
   *Or connect your GitHub repository to Vercel and set the "Root Directory" to `frontend/nextjs-app`.*

### Environment Variables on Vercel
Ensure you set the following in your Vercel Project Settings:
- `BACKEND_URL`: `https://api-handler-zkzefofekg.ap-southeast-1.fcapp.run`
- `NEXT_PUBLIC_API_URL`: (Optional, if used in client-side code)

---

## 3. Maintenance

### Updating Credentials
If you change your Model Studio API key or OSS bucket:
1. Update `backend/update_credentials.py`.
2. Run `python backend/update_credentials.py`.
3. Redeploy backend: `cd backend && s deploy`.

### Local Testing
To test locally:
1. Backend: Run your orchestrator handler locally (if configured).
2. Frontend: `cd frontend/nextjs-app && npm run dev`.
