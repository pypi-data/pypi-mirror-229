import base64
import http.client
import json
import logging
import os
import pathlib
import ssl
from ssl import SSLCertVerificationError

from pySTid.stidresponse import STidAPI_response

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class STidAPI:
    custom_success_codes = (20, 23, 25, 29, 36, 39, 50, 71, 85, 93, 96, 606, 608)

    def __init__(self):
        # self.token = None
        # self.site_id = None
        # self.config_id = None
        self.sslContext = self._sslContext()

    @staticmethod
    def _sslContext():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cafile=os.path.join(pathlib.Path(__file__).parent.resolve(), "stidmobile-id-com-chain.pem"))
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        return context

    @staticmethod
    def _b64encode(text: str):
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def _b64decode(text: str):
        return base64.b64decode(text.encode()).decode()

    def _request(self, method: str, url: str, body: str = "", headers: dict = None, token: str = None):
        log.debug(f"Sending {method} request to /{url}...")
        host_port = 9092
        host_url = "secure.stidmobile-id.com"
        if headers is None:
            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer ' + token or ""}
        conn = http.client.HTTPSConnection(host_url, host_port, context=self.sslContext)
        try:
            conn.request(method=method, url="/" + url, body=body, headers=headers)
            response = conn.getresponse()
        except http.client.BadStatusLine as e:
            custom_code = int(e.args[0][9:12])
            custom_message = e.args[0][13:-2]
            success = custom_code in STidAPI.custom_success_codes
            if success:
                log.debug(f"Response: {custom_code} - {custom_message}")
            else:
                log.warning(f"Response: {custom_code} - {custom_message}")
            return STidAPI_response(success=success, status_code=custom_code, content={'Message': custom_message})
        except SSLCertVerificationError as e:
            log.error(f"SSLCertVerificationError: {e.verify_message}")
            return STidAPI_response(success=False, status_code=0, content={'error': e.args})
        except Exception as e:
            log.error(f"Response: {e.args}")
            return STidAPI_response(success=False, status_code=0, content={'error': e.args})
        code = response.getcode()
        data = response.read().decode()
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            if data[:15] == "<!DOCTYPE html>":
                # data = data.replace("\r\n", "")
                log.error(f"Response: {code} - HTML received")
                return STidAPI_response(success=False, status_code=code, content={'error': 'HTML page received'})
            else:
                log.error(f"Response: json decode error - {data}")
                return STidAPI_response(success=False, status_code=code, content={'error': 'json decode error'})
        success = 199 < code < 300
        if success:
            log.debug(f"Response: {code} - {data}")
        else:
            log.warning(f"Response: {code} - {data}")
        return STidAPI_response(success=success, status_code=code, content=json_data)

    # def quick_init(self, client_id: str, client_secret: str, site_name: str, config_name: str):
    #     if not (t := self.get_token(client_id, client_secret)):
    #         return t
    #     self.token = t.content['access_token']
    #     if not (s := self.set_site(site_name=site_name, token=self.token)):
    #         return s
    #     if not (c := self.set_config(config_name=config_name, token=self.token)):
    #         return c
    #     log.info("Successfully initialised API")
    #     return t

    def get_siteAuth(self, client_id: str, client_secret: str, site_name: str, config_name: str):
        if not (token := self.get_token(client_id=client_id, client_secret=client_secret)):
            return token
        token = token.content['access_token']
        if not (site := self.get_site_id(site_name=site_name, token=token)):
            return site
        site_id = site.content
        if not (config := self.get_config_id(config_name=config_name, site_id=site_id, token=token)):
            return config
        config_id = config.content
        log.info("Successfully created siteAuth token")
        return STidAPI._b64encode(json.dumps({"token": token, "site_id": site_id, "config_id": config_id}))

    def renew_siteAuth(self, siteAuth, client_secret: str, client_id: str = None):
        siteAuth = STidAPI._decode_siteAuth(siteAuth)
        if client_id is None:
            client_id = json.loads(STidAPI._b64decode(siteAuth['token'].split(".")[1]))['client_id']
        if not (r := self.get_token(client_id=client_id, client_secret=client_secret)):
            return r
        siteAuth['token'] = r.content['access_token']
        log.info(siteAuth['token'])
        return STidAPI._b64encode(json.dumps(siteAuth))

    @staticmethod
    def _decode_siteAuth(siteAuth: str):
        return json.loads(STidAPI._b64decode(siteAuth))

    def get_token(self, client_id: str, client_secret: str):
        b46auth = STidAPI._b64encode(f"{client_id}:{client_secret}")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + b46auth
        }
        return self._request(method="POST", url="token", body="grant_type=client_credentials&scope=global", headers=headers)

    def get_sites(self, siteAuth: str = None, token: str = None):
        if siteAuth:
            token = STidAPI._decode_siteAuth(siteAuth)['token']
        return self._request(method="GET", url="api/GetSiteListV1/", token=token)

    def get_site_id(self, site_name: str, siteAuth: str = None, token: str = None):
        if not (r := self.get_sites(siteAuth=siteAuth, token=token)):
            return r
        site_id = next((item['SiteId'] for item in r.content if item["SiteName"] == site_name), None)
        if site_id is None:
            r.success = False
            r.content = {'Message': f"Site \"{site_name}\" not found"}
            return r
        r.content = site_id
        return r

    def get_configs(self, site_id: int, siteAuth: str = None, token: str = None):
        if siteAuth:
            siteAuth = STidAPI._decode_siteAuth(siteAuth)
            token = siteAuth['token']
            site_id = siteAuth['site_id']
        return self._request(method="GET", url=f"api/GetReaderConfigurationListV1/?siteId={site_id}", token=token)

    def get_config_id(self, config_name: str, siteAuth: str = None, token: str = None, site_id: int = None):
        if not (r := self.get_configs(site_id=site_id, siteAuth=siteAuth, token=token)):
            return r
        config_id = next((item['ConfigurationId'] for item in r.content if item["ConfigurationName"] == config_name), None)
        if config_id is None:
            r.success = False
            r.content = {'Message': f"Config \"{config_name}\" not found"}
            return r
        r.content = config_id
        return r

    def get_credits(self, siteAuth: str = None, token: str = None, available: bool = False):
        if siteAuth:
            token = STidAPI._decode_siteAuth(siteAuth)['token']
        return self._request(method="GET", url="api/GetAvailableCreditsV1/" if available else "api/GetReservedCreditsV2/", token=token)

    def get_cards(self, site_id: int = None, token: str = None):
        return self._request(method="GET", url=f"/api/GetVirtualCardListV2/?siteId={site_id}", token=token)

    def get_card(self, card_id: int, site_id: int = None, token: str = None):
        return self._request(method="GET", url=f"api/GetVirtualCardDetailV2/?siteId={site_id}&vcardId={card_id}", token=token)

    def get_card_by_email(self, email: str, site_id: int = None, token: str = None):
        resp = self.get_cards(site_id, token)
        if not resp.success:
            return resp

        if isinstance(resp.content, list):
            for card in resp.content:
                if 'Email' and 'VirtualCardId' in card:
                    if email.lower() == str(card['Email']).lower():
                        return STidAPI_response(True, 1, card)

        return STidAPI_response(False, -1, "No cards found")

    def add_card(self, first_name: str, last_name: str, email: str, card_code: str, site_id: int = None, config_id: str = None, token: str = None):
        body = json.dumps({
            "siteId": site_id or "",
            "ConfigurationId": config_id or "",
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "PrivateorStidId": card_code
        })
        return self._request(method="POST", url="api/AddVirtualCardV2/", body=body, token=token)

    def _process_cards(self, card_ids: list | int, url: str, action: str, site_id: int = None, token: str = None):
        body = json.dumps({
            "siteId": site_id or "",
            "ids": card_ids if type(card_ids) is list else (card_ids,)
        })
        if r := self._request(method="POST", url=url, body=body, token=token):
            for card in r.content['responseMessage']:
                if card['StatusCode'] in STidAPI.custom_success_codes:
                    log.info(f"Card {card['VirtualCardId']} {action} successful: {card['ResponseMessage']}")
                else:
                    log.warning(f"Card {card['VirtualCardId']} {action} failed: {card['ResponseMessage']}")
                    r.success = False
            if type(card_ids) is list:
                r.content = r.content['responseMessage']
            else:
                r.content = r.content['responseMessage'][0]
        return r

    def send_card(self, card_ids: int | list, site_id: int = None, token: str = None):
        return self._process_cards(card_ids=card_ids, url="api/SendVirtualCardV1/", action="Send", site_id=site_id, token=token)

    def revoke_card(self, card_ids: int | list, site_id: int = None, token: str = None):
        return self._process_cards(card_ids=card_ids, url="api/RevokeVirtualCardV1/", action="Revoke", site_id=site_id, token=token)

    def delete_card(self, card_ids: int | list, site_id: int = None, token: str = None):
        return self._process_cards(card_ids=card_ids, url="api/DeleteVirtualCardV1/", action="Delete", site_id=site_id, token=token)

    def remove_card(self, card_id: int | list):
        pass


