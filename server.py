from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {'state': 'Слона'}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

        res['response']['text'] = f'Привет! Купи {sessionStorage["state"].lower()}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    for word in ('ладно', 'куплю', 'покупаю', 'хорошо'):
        if word in req['request']['original_utterance'].lower():
            res['response']['text'] = f'{sessionStorage["state"]} можно найти на Яндекс.Маркете!'
            if sessionStorage['state'] == 'Кролика':
                res['response']['end_session'] = True
            else:
                sessionStorage['state'] = 'Кролика'
            return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage['state'].lower()}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={sessionStorage['state'].lower()[:-1]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
