# moodproject
Mood application for NeuroFlow design challenge. See runtime details after answer to prompt.

#Prompt
"Document what, if anything, you would do differently if this were a production application and
not an assessment? What tech would you use? How would you handle things differently if it
needed to handle more users, more data, etc?"

#Answer
If this were a production application, I'd have a couple security concerns to address. Namely, the user's token is sent back to the ajax call as an unencrypted string and simply stored in local storage. There's also the issue of the Firebase authentication information being stored publicly in my GitHub in the .json config files.

I also have localhost hardcoded for testing purposes. This would need to change.

As for the UI/UX, I attempted to make the home and login pages fairly nice, although the html returned from the /mood endpoint is plaintext and quite ugly. The website needs some form of navigation (menu) and the ability to jump right from the home page to the /mood endpoint if the user is already logged in. The /mood endpoint itself would do well with a sleek, dynamic graph and calendar selector to show the streaks for a given week, month, or year. There is so much that could be improved upon with the design of the /mood endpoint that would make the data more readable for the user.

As for the tech I would use, I would need to deploy the final product to a production WSGI server. mod_wsgi (see here: https://modwsgi.readthedocs.io/en/master/) is a great module for hosting a Flask app. Of course that means we'd have to set up an Apache server, preferably on some Linux distribution.

With regard to scalability, the algorithm for checking what posts correspond to which users is quite slow when given a large dataset. Storing the entire root data pull from the DB and iterating over it as a JSON object (rather than calling a ref.get() to each child) would speed things up. Parallelizing this process would also help. With an upgrade to the Blaze plan in Firebase, I can add more databases for storing more mood pushes. Preferably, the users would be grouped alphabetically across multiple databases to make searching faster. The free Firebase plan also only allows 100 simulataneous users. Upgrading this plan would allow for more. Alternatively, we could use AWS for greater security and services just host our own SQL server.

#Important Notes
- I modified \moodproject\venv\Lib\site-packages\firebase_admin\_http_client.py due to an issue with an outdated urllib3 package (see: https://stackoverflow.com/questions/56212844/how-to-fix-firebase-admin-error-typeerror-init-got-an-unexpected-keyword). Make sure that if you choose to ignore the venv, you replace this file.
- For the /mood endpoint, streaks are output as a list of dictionaries. Each dict has a key, which is the date in YYYYMMDD format, and the streak number as the value.
- You must navigate the frontend as follows: home page -> login/signup -> mood
- The /mood endpoint uses bearer authentication. If you'd like to use an online API tester (if you somehow manage to get your token in plaintext), take this into consideration
- The link to the Firebase realtime database is as follows: https://mood-c9d58-default-rtdb.firebaseio.com/
- If you have trouble signing up for my Firebase project (creating a user), contact me at acp328@drexel.edu
- Login/signup page will let you know what went wrong if there is an error via an alert banner
- Nicepage was used to create the frontend web pages for the home and login pages for a sleek design

