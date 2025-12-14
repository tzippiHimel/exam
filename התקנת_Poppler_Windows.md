# התקנת Poppler ב-Windows

Poppler נדרש לעיבוד קבצי PDF. אם אתה מקבל שגיאה "Unable to get page count. Is poppler installed and in PATH?", בצע את השלבים הבאים:

## שלב 1: הורדת Poppler

1. לך ל: https://github.com/oschwartz10612/poppler-windows/releases/
2. הורד את הגרסה האחרונה (למשל: `Release-XX.XX.X-X.zip`)
3. חלץ את הקובץ לתיקייה (למשל: `C:\poppler`)

## שלב 2: הוספה ל-PATH

### אופציה A: זמני (רק לסשן הנוכחי)

פתח PowerShell והרץ:
```powershell
$env:PATH += ";C:\poppler\Library\bin"
```

**חשוב:** זה יעבוד רק בטרמינל הנוכחי. אם תסגור את הטרמינל, תצטרך להריץ שוב.

### אופציה B: קבוע (מומלץ)

1. לחץ `Win + R`
2. הקלד `sysdm.cpl` ולחץ Enter
3. לחץ על הכרטיסייה "Advanced"
4. לחץ על "Environment Variables"
5. בחלק "System variables", בחר "Path" ולחץ "Edit"
6. לחץ "New" והוסף: `C:\poppler\Library\bin`
7. לחץ "OK" בכל החלונות
8. **הפעל מחדש את הטרמינל** (או את המחשב)

## שלב 3: בדיקה שההתקנה עבדה

פתח PowerShell חדש והרץ:
```powershell
pdftoppm -h
```

אם אתה רואה הודעת עזרה, ההתקנה הצליחה! ✅

## שלב 4: הפעלה מחדש של השרת

אחרי הוספת Poppler ל-PATH:
1. עצור את השרת (Ctrl+C)
2. הפעל מחדש את השרת
3. נסה להעלות PDF שוב

## פתרונות חלופיים

אם אתה לא רוצה להתקין Poppler:

1. **המר PDF לתמונות:**
   - פתח את ה-PDF
   - שמור כל עמוד כתמונה (PNG או JPG)
   - העלה את התמונות במקום ה-PDF

2. **השתמש בקובץ טקסט:**
   - העתק את התוכן מה-PDF
   - שמור כקובץ `.txt`
   - העלה את קובץ הטקסט

3. **השתמש ב-Docker:**
   - Poppler מותקן אוטומטית ב-Docker
   - הרץ: `docker-compose up --build`

## בעיות נפוצות

### "pdftoppm is not recognized"
- ודא שהוספת את הנתיב הנכון ל-PATH
- ודא שהטרמינל הופעל מחדש
- נסה נתיב מלא: `C:\poppler\Library\bin\pdftoppm.exe -h`

### עדיין לא עובד אחרי ההתקנה
- ודא שהשרת הופעל מחדש
- בדוק שהנתיב נכון (התיקייה `bin` צריכה להכיל `pdftoppm.exe`)
- נסה להריץ את השרת מהטרמינל שבו הוספת את Poppler ל-PATH

