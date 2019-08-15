help:
	@egrep "^\w+:" Makefile

build_py_venv:
	virtualenv -p python3.7 env

install_py_dependencies: build_py_venv
	env/bin/pip install -r requirements.txt

run_app:
	env/bin/python app.py

package:
	cd .. && zip -rFS --exclude=*/.git/* --exclude=*/.gitignore --exclude=*/var/* --exclude=*/.idea/* --exclude=*/env/* --exclude=*.iml --exclude=*/__pycache__/* imdb-web.zip imdb-web

deploy_project_to_aws:
	echo "Remember to upgrade Python modules"
	#sleep 10
	rsync --archive --compress --recursive --delete --exclude=.git --exclude=.gitignore --exclude=.idea --exclude=*.iml --exclude=env --exclude=var --exclude==__pycache__ --exclude=*.pyc -e "ssh -i ~/.ssh/zuya-reddit.pem" . ubuntu@redditor-view.zuya.im:/home/ubuntu/imdb-web
	ssh -i ~/.ssh/zuya-reddit.pem ubuntu@redditor-view.zuya.im 'sudo systemctl restart redditor-view.service'
