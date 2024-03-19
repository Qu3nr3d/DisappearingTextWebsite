from flask import Flask, session, flash, redirect, url_for, request, render_template
from flask_bootstrap import Bootstrap5
from flask_socketio import SocketIO
import threading
import smtplib
import requests


app = Flask(__name__)
app.secret_key = '123456789QAZWSX'
bootstrap = Bootstrap5(app)
socketio = SocketIO(app)
current_sleep_thread = None
current_text = ''
PASSWD = 'YOUR_EMAIL_PASSWD'
EMAIL = "YOUR_EMAIL"
EMAIL_API_KEY = "API_KEY"


def sleep_counter(text):
    global current_sleep_thread, current_text
    current_text = text
    if current_sleep_thread and current_sleep_thread.is_alive():
        current_sleep_thread.cancel()
    socketio.emit('redirect', {'url': '/result'})
    current_sleep_thread = None


def check_mail(mail):
    params = {
        'api_key': EMAIL_API_KEY,
        'email': f'{mail}'
    }

    response = requests.get('https://emailvalidation.abstractapi.com/v1/', params=params)
    deliverable = response.json()['deliverability']
    if deliverable == 'DELIVERABLE':
        return True
    else:
        return False


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/write')
def write():
    return render_template('write.html')


@socketio.on('text_update')
def handle_text_up(data):
    text = data['text']
    global current_sleep_thread

    if text != '':
        if current_sleep_thread and current_sleep_thread.is_alive():
            current_sleep_thread.cancel()
        current_sleep_thread = threading.Timer(5, lambda: sleep_counter(text))
        current_sleep_thread.start()


@app.route('/result')
def result():
    global current_text
    return render_template('result.html', text=current_text)


@app.route('/send', methods=['POST', 'GET'])
def email():
    msg = request.args.get('msg')
    if request.method == 'POST':
        mail = request.form.get('email')
        if check_mail(mail):
            with smtplib.SMTP('smtp.gmail.com', timeout=120, port=587) as connection:
                connection.starttls()
                connection.login(user=EMAIL, password=PASSWD)
                connection.sendmail(from_addr=EMAIL, to_addrs=mail,
                                    msg="Subject: Your dangerous text is here! \n\n"
                                        "Here are your text made with your blood and tears:\n"
                                        f"{msg}")
                session.pop('message', None)
            return redirect(url_for('main_page'))

        else:
            flash("That email does not exist, please try again")
            redirect(url_for('email', text=msg))
    return render_template('mail.html', text=msg)


if __name__ == '__main__':
    app.run()
