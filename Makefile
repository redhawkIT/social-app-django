build:
	@ python setup.py sdist
	@ python setup.py bdist_wheel --python-tag py2
	@ BUILD_VERSION=3 python setup.py bdist_wheel --python-tag py3

publish:
	@ python setup.py sdist upload
	@ python setup.py bdist_wheel --python-tag py2 upload
	@ BUILD_VERSION=3 python setup.py bdist_wheel --python-tag py3 upload

clean:
	@ find . -name '*.py[co]' -delete
	@ find . -name '__pycache__' -delete
	@ rm -rf *.egg-info dist build

docker-tox-build:
	@ docker inspect omab/psa-social-app-django >/dev/null 2>&1 || ( \
		docker build -t omab/psa-social-app-django . \
	)

docker-tox: docker-tox-build
	@ docker run -it --rm \
		--name psa-social-app-django-test \
		-v "`pwd`:/src" \
		omab/psa-social-app-django tox
