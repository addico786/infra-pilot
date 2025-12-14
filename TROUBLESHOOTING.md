# Frontend Troubleshooting Guide

## If you can't see the frontend:

### 1. Check if Vite dev server is running
```bash
cd frontend
npm run dev
```

You should see output like:
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://0.0.0.0:5173/
```

### 2. Check the correct URL
- **From Windows browser**: `http://localhost:5173`
- **From WSL terminal**: `http://localhost:5173` or `http://0.0.0.0:5173`

### 3. Check browser console
Press F12 in your browser and check:
- **Console tab**: Look for errors (red text)
- **Network tab**: Check if files are loading (should see 200 status)
- **Elements tab**: Check if `<div id="root">` exists and has content

### 4. Common Issues:

#### Issue: Blank white page
**Solution**: 
- Open browser console (F12)
- Check for JavaScript errors
- Verify React is mounting (should see `[Main] React app mounted` in console)

#### Issue: "Cannot GET /"
**Solution**: 
- Make sure you're accessing `http://localhost:5173` (not port 8000)
- Check if Vite is running on a different port (check terminal output)

#### Issue: Network error / Connection refused
**Solution**:
- Make sure Vite dev server is running
- Try `http://127.0.0.1:5173` instead of `localhost`
- Check Windows Firewall isn't blocking the port

#### Issue: Files not loading (404 errors)
**Solution**:
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Restart Vite dev server

### 5. Quick Test
Open browser console (F12) and type:
```javascript
document.getElementById('root')
```

If it returns `null`, the HTML isn't loading. If it returns an element, React should be mounting.

### 6. Verify React is working
You should see these console logs:
- `[Main] Starting React app...`
- `[Main] React app mounted`
- `[App] Component rendered`

If you don't see these, React isn't mounting.

### 7. WSL-Specific Issues
If running in WSL:
- Make sure you're accessing from Windows browser (not WSL browser)
- Use `http://localhost:5173` (WSL forwards localhost to Windows)
- If that doesn't work, try the WSL IP address shown in Vite output

### 8. Reinstall dependencies (last resort)
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

