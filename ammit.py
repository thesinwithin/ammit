#!/usr/bin/python

import uuid
from bottle import Bottle, run, request, SimpleTemplate, redirect
import redis

tpl_add_get = SimpleTemplate('''
        <html>
            <head>
	            <title>Ammit</title>
            </head>
            <body>
                <br /> <br />
                <form action="/add" method="post" name="ammit">
                <p style="text-align: center;"><input name="url" size="64" type="url" /></p>
                <p style="text-align: center;"><input name="submit" type="submit" value="Make it short!" /></p>
                </form>
            </body>
        </html>
        ''')

tpl_add_post = SimpleTemplate('''
        <html>
            <head>
	            <title>Ammit</title>
            </head>
            <body>
                <br />
                <p style="text-align: center;"><span style="font-family:arial,helvetica,sans-serif;">URL </span></p>
                <p style="text-align: center;"><span style="font-family:arial,helvetica,sans-serif;">{{url}}</span></p>
                <p style="text-align: center;"><span style="font-family:arial,helvetica,sans-serif;">has been shortened to </span></p>
                <p style="text-align: center;"><span style="font-family:arial,helvetica,sans-serif;">{{res}}</span></p>
                <p style="text-align: center;"><span style="font-family:arial,helvetica,sans-serif;">and can be accessed at: </span></p>
                <p style="text-align: center;"><span style="font-family:arial,helvetica,sans-serif;">{{new_url}}</span></p>
            </body>
        </html>
        ''')

tpl_default = SimpleTemplate('''
        <html>
            <head>
	            <title>Ammit</title>
	        </head>
            <body>
            <br/>
            <p style="text-align: center;"><font face="arial, helvetica, sans-serif">No URL id entered. Make a request with a valid one, or add a new one at /add.</font></p>
            </body>
        </html>
        ''')

tpl_invalid_req = SimpleTemplate('''
        <html>
            <head>
	            <title>Ammit</title>
	        </head>
            <body>
            <br/>
            <p style="text-align: center;"><font face="arial, helvetica, sans-serif">No such URL id. Make a request with a valid one, or add a new one at /add.</font></p>
            </body>
        </html>
        ''')

app = Bottle()

def ss(url):
    """Shorten & Store"""
    res = str(uuid.uuid5(uuid.NAMESPACE_URL, url)).split('-')[4]
    rcon = redis.Redis(host='localhost', port=6379)
    rcon.set(res,url)
    return res

@app.route('/')
def default():
    return tpl_default.render()


@app.route('/add', method='GET')
def show_form():
    return tpl_add_get.render()

@app.route('/add', method='POST')
def process_form():
    url = request.forms.get('url')
    res = ss(url)
    new_url = str(request.urlparts[0])+"://"+str(request.urlparts[1])+"/"+str(res)
    return  tpl_add_post.render(url=url, res=res, new_url=new_url)

@app.route('/<url_id>')
def redirect_url(url_id):
    try:
        rcon = redis.Redis(host='localhost', port=6379)
        res = rcon.get(url_id)
        redirect(res)
    except:
        return tpl_invalid_req.render()

run(app, host='0.0.0.0', port=8080)