#!/usr/local/bin/python3.8
# script: compound interest on ftx.com
# author: bert2002 
# notes:

import os
import time
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import hmac

from pushover import init, Client

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

client = FtxClient(api_key=os.environ.get("FTX_API_KEY", None), api_secret=os.environ.get("FTX_SECRET", None))
init(os.environ.get("PUSHOVER_APP_KEY", None))

coins = os.environ.get("COINS", None).split(",")
balances = client._get("wallet/balances")
for balance in balances:
	if balance["coin"] in coins:
		total_bal = balance["total"]
		print("lending out %s %s" % (total_bal, balance["coin"]))

		try:
			client._post(
				"spot_margin/offers",
				{
				"coin": balance["coin"],
				"size": total_bal,
				"rate": 0.000006,
				},
			)
			Client(os.environ.get("PUSHOVER_USER_KEY", None)).send_message('<b>%s</b>: %s' % (balance["coin"],total_bal), title="FTX COMPOUNDING", html=1)
		except Exception as e:
			print("Fail to resubmit lending offer", str(e))
			Client(os.environ.get("PUSHOVER_USER_KEY", None)).send_message('FAILED <b>%s</b>: %s' % (balance["coin"],str(e)), title="FTX COMPOUNDING", html=1)


