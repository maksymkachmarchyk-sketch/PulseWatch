# PulseWatch frontend (HTML + Bootstrap)
1. У `js/app.js` змініть `API` на адресу бекенду (за замовчуванням http://localhost:8000).
2. Запуск:  `cd frontend && python -m http.server 5173`  ->  http://localhost:5173/login.html
3. У .env бекенду: FRONTEND_BASE_URL=http://localhost:5173 та CORS_ALLOWED_ORIGINS=http://localhost:5173
