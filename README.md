# Django Blog

Multi-user Blog website built with ```Django 3.2.12``` and ```Bootstrap 5.1.3```

My aim of creating this website is to build a free and easy to use website where we, the Django developers, can share tuorials, tips & tricks, best practices and experience about Django on a site built with with Django.

<strong>If you want to share what you learned to help others and yourself, please consider
 contributing to the project, either in development or by writing posts after it has been deployed. </strong>

We can consider it as a FREE (Only for Django developers) alternative to Medium.com or Dev.to

If you like the idea or found the project helpful, consider ```forking``` and ```Giving stars```.

## Features
- Multi user
- Email verification
- Profile for users
- Bookmark posts (soon)
- Social login (soon)
- Follow and Following (soon)
- Draft and Published posts
- CRUD posts with permission
- Custom user model with email login
- Bootstrap for front end


## How to use

- You need to have your own django project first

- Clone this  repo
```
git clone https://github.com/balewgize/django-blog.git
```

- Navigate to django_blog directory
```
cd django_blog
```

- Create Virtual environment and activate it
```
python3 -m venv venv
```
```
source venv/bin/activate (Linux or MacOS)
```
```
.\venv\Scripts\activate (Windows)
```

- Install required packages
```
pip install -r requirements.txt
```

## Provide credentials in .env file
- Create a file named .env inside django_blog folder (the project root dir)

- Provide credentials in key=value format without qoutes as follows
```
DB_NAME=name
DB_USER=user
DB_PASS=password

# Django credentials
SECRET_KEY=your django project secret key
DEBUG=True

# Email credentials
EMAIL_USER=email address
EMAIL_PASS=eamil password
```

<strong>Note: </strong> If you are using Gmail, you need to create 
<a href="https://myaccount.google.com/apppasswords">Google App Password </a> that
will be used as in place of email password

## Create super user and start the server
```
python manage.py createsuperuser
```

- Login to admin site and add few post categories
(Post categories are managed by the admin only, writers can only select)

```
python manage.py runserver
```

Enjoy our website :)