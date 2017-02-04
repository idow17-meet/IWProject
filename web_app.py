from flask import Flask, render_template, request, redirect, url_for, flash, g
app = Flask(__name__)
app.secret_key = 'i love potatoes'
from flask import session

from database_setup import *

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

from flask_oauth import OAuth
import json

#SECRET
#Client id: 606083212870-invusvesj5a2khknk813hrupq27h35k6.apps.googleusercontent.com 
#client secret:  0Wbve1W1lOrRvoUquT4SFq2k 


GOOGLE_CLIENT_ID = '606083212870-invusvesj5a2khknk813hrupq27h35k6.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '0Wbve1W1lOrRvoUquT4SFq2k'
REDIRECT_URI = '/oauth2callback'

oauth = OAuth()

google = oauth.remote_app('google',
                      base_url='https://www.google.com/accounts/',
                      authorize_url='https://accounts.google.com/o/oauth2/auth',
                      request_token_url=None,
                      request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                            'response_type': 'code'},
                      access_token_url='https://accounts.google.com/o/oauth2/token',
                      access_token_method='POST',
                      access_token_params={'grant_type': 'authorization_code'},
                      consumer_key=GOOGLE_CLIENT_ID,
                      consumer_secret=GOOGLE_CLIENT_SECRET)

def sort_leaderboards(scores):
	# bubble sort but with leaderboards
	# inefficient but what can i do :)
	for j in range(len(scores) - 1, -1, -1):
		for i in range(j):
			if (scores[i].score < scores[i + 1].score):
				scores[i], scores[i + 1] = scores[i + 1], scores[i]


@app.route('/')
def index():

    access_token = session.get('access_token')
    if access_token is None:
    	return redirect(url_for('login'))
 
    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError
 
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
 
    jsonstring = res.read()
    name = json.loads(jsonstring)['name']
    email = json.loads(jsonstring)['email']
    photo = json.loads(jsonstring)['picture']
    session['json'] = jsonstring
    session['user_id'] = json.loads(jsonstring)['id']
    return render_template('main.html', name=name, email=email, photourl=photo)
 
 
@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)
 
@app.route('/logout')
def logout():
	if not (session.get('access_token', None) is None):
		session.pop('access_token')
	return redirect(url_for('login'))
 
 
@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))
 
 
@google.tokengetter
def get_access_token():
    return session.get('access_token')

    

@app.route('/Leaderboards')
def leaderboards():
	scores = list(dbsession.query(ScoreInfo))
	sort_leaderboards(scores)
	return render_template('leaderboards.html', scores=scores)


@app.route('/Get-highscore')
def get_highscore():
	user_id = session.get('user_id')
	if user_id is None:
		flash('You were redirected to the main page since you arent logged in.')
		return redirect(url_for('index'))
	score = dbsession.query(ScoreInfo).filter_by(userid=user_id).first()
	return str(score.score)

# Games:
@app.route('/Flappy-Moshe')
def flappy_moshe():
	return render_template('flappy_moshe.html')
if __name__ == '__main__':
	app.run(debug=True, threaded=True)

