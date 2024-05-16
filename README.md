Overview:

The Learnease website is intended to demonstrate full-stack development technologies.  It is for academic purposes and not intended to be deployed.  

Getting started on Windows:

1. Clone the git repository

2. conda env create -f environment.yml

3. Activate the taskerr conda environment:

	pip install djangorestframework

	pip install youtube-search-python

	python -m pip install Pillow 

5. Run migrations:

	python manage.py migrate

6. Create the superuser to log on:

	python manage.py createsuperuser

	If you get a TTY error: 

	winpty python manage.py createsuperuser
7. Create a course through admin page
8. Launch the Website.  You will be directed to log on.  After you log on, you should be directed to the main page for learnease.  If not, click on visit site.
9. Explore the Site 
Thankyou
