# Project Overview

Project of course CS50x https://web.archive.org/web/2/https://cs50.harvard.edu/web/2020/projects/final/capstone/

ConnectionCards is a dating website designed to make you find meaningful connections. It is similar to e.g. Tinder with the distinction that you will not waste hours swiping through profiles since you are limted to two (2) likes per day.

This forces you to be thoughtful with your matches, and encourages building genuine connection. Every day at the same time you will have new potential profiles waiting for you.

The site offers all functionality that one can expect including
- Profile pictures
- Gender preferences
- Matches limited to your selected city
- A responsive chat
- Ability to unmatch with matches
- Mobile responsiveness

# Distinctiveness and Complexity


This project used Django with 4 database models as backend, and used Vanilla Javascript in frontend.

It took considerably more time to develop than previous projects and is different from these, including techniques not used in previous projects.

It has multiple complex parts including
- Possibility to upload images which are automatically re-scaled before being saved on server
- A self-developed complex but fast filtering algorithm to help you select your city
- A beautiful frontend with CSS based animations
- A chat using long-running http requests instead of polling to get new messages
- A long-running background task to run matchmaking process daily
- A match-making process that takes gender preference into account as well as tries to ensure people with few candidates presented are prioritized

# How to run application
Install Pillow (see requirements.txt)

python ./manage.py makemigrations &&
python ./manage.py migrate --run-syncdb


optional:
python ./manage.py create_test_data

python ./manage.py runserver

Now the server is running.

Start background thread for matchmaking by enter the root /start_background_matching, e.g. http://127.0.0.1:8000/start_background_matching
The task will run daily at the time (UTC) specified in SWITCHING_TIME of util_matching.py

Start using the website! To see an example created by created_test_data log in with User: adam@example.com  PW: test

# Files of the project

## ConnectionCards/app/cities5000.txt
A list of all cities in the world with a population > 5000. Source https://download.geonames.org/export/dump/

admin1CodesASCII.txt and admin2Codes.txt is similarly used to make sense of the data in cities5000.txt

## ConnectionCards/app/management/commands
create_test_data.py - Generates some data for testing the application
createtomorrowsmatches.py - Command to force the matchmaking process to run for testing purposes

## ConnectionCards/app/models.py
Models used.
- User
- UserProfile (profile of user, including biography, preferences etc)
- HalfPairing (A pair of these is created when matchmaking process runs, includes info about if current user swiped right on potential match etc)
- ChatMessage

## ConnectionCards/app/static/app/*.js
chat.js - JS for Chat page
match.js - JS for matching page
profile.js - JS for profile page


## ConnectionCards/app/static/app/styles.css
Most CSS of the project

ConnectionCards/app/templates/app/*.html

All HTML pages are rendered using Django, and inherits from layout.html or login_layout.html

- chat.html - Chat page
- layout.html - Shared parts including banner
- login.html - Login page
- login_layout.html - Shared parts witout banner
- match.html - Main page where the user can match with others
- profile_view.html - Page to edit user's profile
- register.html - Registering page

## ConnectionCards/app/static/app/images/logo.png
Logo of application (made using some AI tool)

## ConnectionCards/app/tests.py
Some unit tests

## ConnectionCards/app/views.py
Main backend implementation, all view functions are implemented here

## ConnectionCards/app/util_matching.py
Implementation of the periodically running matchmaking process, and the code that makes this run periodically

## ConnectionCards/dev_server.ps1
Script to run a few tests and then set up a test environment

## ConnectionCards/media/images/placeholder.png
Default profile picture (made using some AI tool)

## ConnectionCards/media/images/*.png
Profile pictures used for example/test users

## README.md
This file

