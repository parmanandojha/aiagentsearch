# ⚠️ VERCEL IS NOT RECOMMENDED FOR DJANGO

The error you're seeing is because **Vercel doesn't support Django applications well**.

## 🚀 RECOMMENDED: Use Railway Instead (5 minutes)

Railway is MUCH better for Django and takes only 5 minutes to deploy:

1. **Go to**: https://railway.app
2. **Sign up** (free, with GitHub)
3. **Click**: "New Project" → "Deploy from GitHub repo"
4. **Select**: Your repository (`parmanandojha/aiagentsearch`)
5. **Add Environment Variable**:
   - Key: `GOOGLE_MAPS_API_KEY`
   - Value: Your Google Maps API key
6. **Railway auto-detects Django** and deploys!
7. **Done!** Your app will be live at `https://your-app.up.railway.app`

**That's it!** Railway handles everything - no configuration needed.

---

## If You Must Use Vercel (Complex & Limited)

Vercel requires:
- Complex serverless function setup (already added but may not work)
- External database (SQLite won't work)
- Static file handling issues
- No WebSocket support
- Cold start delays

### Steps to Try (May Still Fail):
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add:
   ```
   GOOGLE_MAPS_API_KEY=your_key
   SECRET_KEY=your_secret_key
   DEBUG=False
   ALLOWED_HOSTS=aiagentsearch.vercel.app,*.vercel.app
   ```
3. Redeploy

**But honestly, just use Railway - it's 100x easier for Django!**

