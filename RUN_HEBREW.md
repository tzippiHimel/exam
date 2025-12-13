# הוראות הרצה - Exam Grading System

## 🚀 איך להריץ את האפליקציה

### שלב 1: התקנת Docker
אם עדיין לא התקנת Docker:
- הורד והתקן [Docker Desktop](https://www.docker.com/products/docker-desktop)
- ודא ש-Docker רץ (האיקון בתפריט)

### שלב 2: קבלת מפתח API של Gemini
1. לך ל: https://makersuite.google.com/app/apikey
2. התחבר עם חשבון Google
3. צור מפתח API חדש
4. העתק את המפתח

### שלב 3: יצירת קובץ .env
צור קובץ בשם `.env` בתיקיית הפרויקט (באותה תיקייה כמו `docker-compose.yml`):

**Windows (PowerShell):**
```powershell
New-Item -Path .env -ItemType File
notepad .env
```

**Windows (CMD):**
```cmd
type nul > .env
notepad .env
```

**Linux/Mac:**
```bash
touch .env
nano .env
```

**תוכן הקובץ `.env`:**
```env
GEMINI_API_KEY=הדבק_את_מפתח_ה-API_כאן
OCR_LANGUAGE=en
MAX_FILE_SIZE_MB=10
```

**חשוב:** החלף `הדבק_את_מפתח_ה-API_כאן` במפתח האמיתי שקיבלת!

### שלב 4: הרצת האפליקציה

פתח טרמינל/CMD/PowerShell בתיקיית הפרויקט והרץ:

```bash
docker-compose up --build
```

**הפעלה ראשונה תארך 5-10 דקות** (הורדת תלויות ומודלים).

### שלב 5: גישה לאפליקציה

לאחר שהכל נטען, פתח בדפדפן:
- **ממשק משתמש**: http://localhost:3000
- **API (תיעוד)**: http://localhost:8000/docs
- **API ישיר**: http://localhost:8000

## 📋 איך להשתמש

1. **העלאת מבחן פתור**: העלה קובץ PDF/תמונה/טקסט עם שאלות ותשובות נכונות
2. **פיענוח**: לחץ "Parse Exam" לחילוץ השאלות
3. **הגשת תשובות**: הזן את תשובות התלמיד
4. **צפייה בתוצאות**: ראה ציונים והסברים

## 🔧 פתרון בעיות

### פורט תפוס?
אם פורט 3000 או 8000 תפוסים:
```bash
# עצור את השירותים
docker-compose down

# שנה פורטים ב-docker-compose.yml
# או עצור את השירות שמשתמש בפורט
```

### שגיאת API?
- ודא שקובץ `.env` קיים ויש בו `GEMINI_API_KEY` נכון
- ודא שהמפתח לא פג תוקף

### שגיאת Build?
```bash
# עצור הכל
docker-compose down

# נקה ובנה מחדש
docker-compose build --no-cache
docker-compose up
```

### בדיקת לוגים
```bash
# לוגים של Backend
docker-compose logs backend

# לוגים של Frontend
docker-compose logs frontend

# כל הלוגים
docker-compose logs
```

### עצירת האפליקציה
```bash
# עצירה רגילה
docker-compose down

# עצירה + מחיקת volumes
docker-compose down -v
```

## ✅ בדיקה שהכל עובד

### בדיקת Backend:
פתח בדפדפן: http://localhost:8000/api/health
צריך לראות: `{"status":"healthy","service":"exam-grading-api"}`

### בדיקת Frontend:
פתח: http://localhost:3000
צריך לראות את הממשק עם כותרת "AI Exam Grading System"

### בדיקת API Docs:
פתח: http://localhost:8000/docs
צריך לראות את Swagger UI עם כל ה-endpoints

## 🎯 דרישות מערכת

- **Docker Desktop** מותקן ורץ
- **מפתח Gemini API** תקין
- **פורטים 3000 ו-8000** פנויים
- **חיבור לאינטרנט** (לשימוש ב-Gemini API)

## 💡 טיפים

- הפעלה ראשונה אורכת זמן בגלל הורדת מודלים של OCR
- ודא שיש מספיק זכרון (לפחות 4GB מומלץ)
- אם יש שגיאות, בדוק את הלוגים עם `docker-compose logs`

## 📞 עזרה נוספת

- קרא את [README.md](./README.md) להנחיות מפורטות
- קרא את [SETUP.md](./SETUP.md) לפתרון בעיות מפורט
- בדוק את [ARCHITECTURE.md](./ARCHITECTURE.md) להבנת המערכת

---

**הכל מוכן!** 🎉
אם יש בעיות, בדוק את הלוגים או פתח issue.

