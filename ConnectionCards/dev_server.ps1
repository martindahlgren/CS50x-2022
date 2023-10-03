if (Test-Path db.sqlite3) {
    # If the file exists, delete it
    Remove-Item db.sqlite3 -Force
}
python ./manage.py makemigrations &&
python ./manage.py migrate && 
python ./manage.py test &&
python ./manage.py create_test_data &&
python ./manage.py runserver