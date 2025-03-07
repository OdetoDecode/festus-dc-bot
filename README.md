# FESTUS
A simple Discord Bot.
### Features
+ Simple chat
+ Polls
+ Reminders
+ Displays welcome messages for new users
+ Small misc functions
### Commands
+ `+hello` or `+hi`
  - Responds with a random greeting
+ `+echo <message>`
  - Deletes your command and repeats the message
+ `+createpoll <time in min> <question> <option1> <option2> ...`
  - Creates user poll with upto 10 options
+ `+remindme DD-MM-YYYY hh:mm <message>`
  - Sends DM at the set time
+ `+dice <N>d<X>`
  - Rolls N dice, each of X sides, and returns sum
+ `+slap @user <reason>`
  - Declares that you slapped the user
### Instructions
+ Change guild id in lib/bot/__init__.py to your server id
+ Change channel ids in bot/__init.py and all cog code files
+ Add token.0 textfile to lib/bot with your own token id in it

### References
Carberra Tutorials
[Youtube](https://www.youtube.com/playlist?list=PLYeOw6sTSy6ZGyygcbta7GcpI8a5-Cooc)
