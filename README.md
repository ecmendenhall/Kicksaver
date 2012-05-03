I made Kicksaver to help out struggling [Kickstarter](http://www.kickstarter.com/) 
projects and practice working with Google App Engine and AJAX. It parses the 
[Ending Soon](http://www.kickstarter.com/discover/ending-soon) and 
[Small Projects](http://www.kickstarter.com/discover/small-projects) categories a few times a day 
to find projects ending soon. This means it won't always be completely up to date, but it should be close.
A working version of the application is available at http://www.kicksaver.com.

Kicksaver was written in Python for Google App Engine. 
The backend requires [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) 
to parse Kickstarter projects, and [Tweepy](https://github.com/tweepy/tweepy) to 
update the Twitter feed. The frontend uses [JQuery](http://jquery.com/) for asynchronous updates, 
fonts from [Google Web Fonts](http://www.google.com/webfonts), 
and CSS styles from [Bootstrap](http://twitter.github.com/bootstrap/). This project is a totally non-commercial
thing not affiliated with Kickstarter in any way. All the code for this project is 
available under an MIT license. For all the details, see the file `LICENSE.md` in
this repository.
