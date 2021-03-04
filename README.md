<h2>Heroku Deployment</h2>
<ul>
<li><code>$ heruko login</code></li>
<li><code>$ git init</code>
<li><code>$ heroku git:remote -a {heroku-project-name}</code></li>
<li><code>$ git add .</code></li>
<li><code>$ git commit -m "first commit"</code></li>
<li><code>$ git push heroku master</code></li>
<li>Start the webhook by running below url</li>
<li>https://manga-uploader.herokuapp.com/setwebhook</li>
</ul>

<h2>Requirments.txt</h2>
<pre>
APScheduler==3.6.3
certifi==2020.12.5
chardet==4.0.0
click==7.1.2
Flask==1.1.2
gunicorn==20.0.4
idna==2.10
itsdangerous==1.1.0
Jinja2==2.11.3
MarkupSafe==1.1.1
python-telegram-bot==13.3
pytz==2021.1
requests==2.25.1
six==1.15.0
tornado==6.1
tzlocal==2.1
urllib3==1.26.3
Werkzeug==1.0.1
</pre>

<h2>gunicorn setup</h2>
<ul>
<li>create "Procfile" named file</li>
<li>Add "web: gunicorn app:app" in Procfile</li>
</ul>
