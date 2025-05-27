pip install -r requirements.txt
python manage.py collectstatic --noinput
npm run dev
python manage.py migrate