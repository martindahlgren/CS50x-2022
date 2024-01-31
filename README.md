# Project Overview

ConnectionCards is a dating website designed to make you find meaningful connections and motivate you to start conversations. It is similar to e.g. Tinder with the distinction that you will not waste hours swiping through profiles.

Instead, each day you are presented with a maximum of four profiles, out of which you can attempt to match with two of them. This forces you to be thoughtful with your matches, and encourages building genuine connection.

Otherwise the site offers all functionality that one can expect including
- Profile pictures
- Gender preferences
- Matches are found in your selected city
- A responsive chat
- Ability to unmatch with matches
- Mobile responsiveness

# Distinctiveness and Complexity

This project took considerably more time to develop than previous projects (~6 months) and is different from these, including techniques not used in these.

It has multiple complex parts including
- 4 database models
- Possibility to upload images which are automatically re-scaled before being saved on server
- A self-developed complex filtering algorithm to ease select the city from 5000 alternatives
- A beautiful frontend with CSS based animations
- A chat using long-running http requests instead of polling to get new messages
- A long-running background task to run matchmaking process daily
- A match-making process that takes gender preference into account as well as tries to ensure people with few candidates presented are prioritized

# How to run application
Install Pillow (see requirements.txt)
In ConnectionCards python ./manage.py runserver

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

