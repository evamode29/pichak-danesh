# پیچک دانش

سامانه ساده آموزشی برای دانش‌آموزان پایه ششم و پنل معلم.

## جهت‌گیری محصول
- ورود دانش‌آموز با کد و رمز
- آزمون هوش تصویری
- آزمون‌ساز و مدیریت آزمون توسط معلم
- امکان تصویر در متن سؤال و گزینه‌ها
- حفظ حساب‌ها و داده‌های فعلی در زمان بازسازی؛ هرگز دیتابیس زنده را با این اسکلت جایگزین نکنید.

## شروع توسعه

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
