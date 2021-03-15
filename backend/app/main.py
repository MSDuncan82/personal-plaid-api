import os
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from plaid.api.item import PublicToken
from config import settings
import plaid
import json
from dotenv import load_dotenv
import logging
load_dotenv()

logging.basicConfig()
logger = logging.getLogger(name=__name__)

jsonify = jsonable_encoder

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))
  
def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

app = FastAPI()

ACCESS_TOKEN = None
PAYMENT_ID = None
ITEM_ID = None
CLIENT = plaid.Client(client_id=settings.PLAID_CLIENT_ID,
                      secret=settings.PLAID_SECRET,
                      environment=settings.PLAID_ENV,
                      api_version='2019-05-29')

@app.post('/api/info')
def info():
  global ACCESS_TOKEN
  global ITEM_ID
  return jsonify({
    'item_id': ITEM_ID,
    'access_token': ACCESS_TOKEN,
    'products': settings.PLAID_PRODUCTS
  })


@app.post('/api/create_link_token')
def create_link_token():
  try:
    response = CLIENT.LinkToken.create(
      {
        'user': {
          # This should correspond to a unique id for the current user.
          'client_user_id': 'user-id',
        },
        'client_name': "Plaid Quickstart",
        'products': settings.PLAID_PRODUCTS,
        'country_codes': settings.PLAID_COUNTRY_CODES,
        'language': "en",
        'redirect_uri': settings.PLAID_REDIRECT_URI,
      }
    )
    pretty_print_response(response)
    return jsonify(response)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))


# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@app.post('/api/set_access_token')
async def get_access_token(request: Request):
  global ACCESS_TOKEN
  global ITEM_ID
  form = await request.form()
  public_token = form["public_token"]
  try:
    exchange_response = CLIENT.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))

  ACCESS_TOKEN = exchange_response['access_token']
  ITEM_ID = exchange_response['item_id']
  return jsonify(exchange_response)
