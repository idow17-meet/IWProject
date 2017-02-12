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
import hashlib

#SECRET
#Client id: 606083212870-invusvesj5a2khknk813hrupq27h35k6.apps.googleusercontent.com 
#client secret:  0Wbve1W1lOrRvoUquT4SFq2k 
#g+ key: AIzaSyAqSCkJphmlRwqDqOMGD9PT7Ld6mF5R5ZI

#My google id:
#103891305576825217486

#Useful:
#sudo lsof -i :5000 | grep "python" | cut -d " " -f3 | xargs kill -9
GOOGLE_CLIENT_ID = '606083212870-invusvesj5a2khknk813hrupq27h35k6.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '0Wbve1W1lOrRvoUquT4SFq2k'
REDIRECT_URI = '/oauth2callback'

oauth = OAuth()

scope = ('https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/plus.login')
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


def md5hash(string):
	return hashlib.md5(string).hexdigest()


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
	session['photo'] = json.loads(jsonstring)['picture']
	session['json'] = jsonstring
	session['user_id'] = json.loads(jsonstring)['id']

	print(jsonstring)
	user_score = dbsession.query(ScoreInfo).filter_by(userid=session['user_id']).first()
	if user_score is None:
		if name == "":
			name = json.loads(jsonstring)['given_name'] + json.loads(jsonstring)['family_name']
		user_score = ScoreInfo(userid=session['user_id'], score=0, name=name)
		dbsession.add(user_score)
		dbsession.commit()
	elif user_score.name == "":
		user_score.name = json.loads(jsonstring)['given_name'] + ' ' + json.loads(jsonstring)['family_name']
		dbsession.commit()
	return render_template('main.html', name=name, email=email, photourl=session['photo'])
 
 
@app.route('/login')
def login():
	callback=url_for('authorized', _external=True)
	return google.authorize(callback=callback)
 
@app.route('/logout')
def logout():
	session.pop('access_token')
	return redirect(url_for('index'))
 
 
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
	indexing = list(range(len((scores))))
	return render_template('leaderboards.html', scores=scores, indexing=indexing, photourl=session['photo'])


@app.route('/Get-highscore/<string:user_id>')
def get_highscore(user_id):
	score = dbsession.query(ScoreInfo).filter_by(userid=user_id).first()
	if score is None:
		return "-1"
	return str(score.score)


@app.route('/Submit-highscore', methods=['GET'])
def submit_highscore():
	userid = request.args.get('userid')
	score = request.args.get('score')
	sent_hash = request.args.get('hash')

	user_score = dbsession.query(ScoreInfo).filter_by(userid=userid).first()
	secret_hash = md5hash(userid + score + app.secret_key)
	if int(request.args.get('score')) > user_score.score and sent_hash == secret_hash:
		user_score.score = score
		dbsession.commit()
	return "gud"


# Games:
@app.route('/Flappy-Moshe')
def flappy_moshe():
	return render_template('flappy_moshe.html', user_id=session['user_id'], photourl=session['photo'])
if __name__ == '__main__':
	app.run(debug=True, threaded=True)

