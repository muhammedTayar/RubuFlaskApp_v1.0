from os import truncate

from django.conf.global_settings import SECRET_KEY
from flask import Flask, render_template, request, flash, url_for
from flask_mail import Mail, Message
from werkzeug.utils import redirect
from flask_recaptcha import ReCaptcha

from settings import *

mail = Mail()
recaptcha = ReCaptcha()

app = Flask(__name__)

app.config.from_object("settings.DevelopmentConfig")

"""
app.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=mail_username,
    MAIL_PASSWORD=mail_password,
    ReCaptcha_site_key=website_schluessel,
    ReCaptcha_secret_key=website_geheim_schluessel
)
"""
app.config.update(
    MAIL_SERVER=app.config["MAIL_SERVER"],
    MAIL_PORT=app.config["MAIL_PORT"],
    MAIL_USE_SSL=app.config["MAIL_USE_SSL"],
    MAIL_USERNAME=app.config["MAIL_USERNAME"],
    MAIL_PASSWORD=app.config["MAIL_PASSWORD"],
    ReCaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"],
    ReCaptcha_secret_key=app.config["RECAPTCHA_SECRET_KEY"],
    SECRET_KEY=app.config["SECRET_KEY"]
)
# get random email address

# Set the secret Site Key an Secret Key for the reCaptcha
#app.config['RECAPTCHA_SITE_KEY'] = RECAPTCHA_SITE_KEY
#app.config['RECAPTCHA_SECRET_KEY'] = RECAPTCHA_SECRET_KEY

# Set the secret key to some random bytes. Keep this really secret!
#app.secret_key = SECRET_KEY


mail = Mail(app)
recaptcha = ReCaptcha(app)

#mail.init_app(app)
#recaptcha.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == "POST":
        if recaptcha.verify():
            name = request.form['name']
            nachname = request.form['nachname']
            organisation = request.form['organisation']
            email = request.form['email']
            telefon = request.form['telefon']
            land = request.form['land']
            subject = request.form['subject']
            msg = request.form['message']

            message = Message(subject, sender="m.tayyar61@gmail.com", recipients=[email])
            message.body = 'Name ist: {} \n Nachname ist: {} \n Organisation ist: {} \n Email ist: {} \n Telefonnummer ist: {} \n Land ist:{} \n Nachricht:{}'.format(
                name, nachname, organisation, email, telefon, land, msg)
            mail.send(message)
            flash("Ihre Anfrag wurde versendet. Sie werden in kürze eine Antwort erhalten!")

            return redirect(request.url)
        else:
            flash("Ihre Anfrage konnte nicht versendet werden. Bitte verifizieren, dass Sie kein Roboter sind!")
    return render_template('index.html')

@app.route('/dokumentation.html')
def documentation():
    return render_template('dokumentation/dokumentation.html')

@app.route('/genindex.html')
def indexkeywords():
    return render_template('dokumentation/genindex.html')

# Derzeit nicht in Benutzung --> Funktionsfaehig
@app.route('/spezifikation.html')
def portfolio_details():
    return render_template('spezifikation.html')

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=80)
