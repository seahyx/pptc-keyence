pip install virtualenv
pip install virtualenvwrapper-win

mkvirtualenv pptc-keyence

workon pptc-keyence

pip install -r requirements.txt

flask db init
flask db migrate -m 'init'
flask db upgrade