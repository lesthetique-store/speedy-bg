import json
import requests


class SpeedyAPI:
    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = "https://api.speedy.bg/v1/",
        language: str = "EN",
    ):
        """
        Initialize with API credentials and default language.
        """
        self.user = username
        self.pwd = password
        self.base = base_url.rstrip("/") + "/"
        self.lang = language

    def _post(self, endpoint: str, data: dict) -> dict:
        """
        Internal helper to send POST requests and parse JSON responses.
        """
        payload = {
            "userName": self.user,
            "password": self.pwd,
            "language": self.lang,
            **data,
        }
        resp = requests.post(self.base + endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()

    def create_shipment(
        self,
        sender: dict,
        recipient: dict,
        service: dict,
        content: dict,
        payment: dict,
        ref1: str = None,
    ) -> dict:
        """
        Create a shipment with all required sections.
        """
        data = {
            "sender": sender,
            "recipient": recipient,
            "service": service,
            "content": content,
            "payment": payment,
        }
        if ref1:
            data["ref1"] = ref1
        return self._post("shipment/", data)

    def print_waybill(self, parcels: list, paper_size: str = "A4") -> bytes:
        """
        Request printing and receive binary PDF data.
        """
        data = {
            "parcels": [{"parcel": {"id": p}} for p in parcels],
            "paperSize": paper_size,
        }
        return requests.post(
            self.base + "print/",
            json={**{"userName": self.user, "password": self.pwd}, **data},
        ).content

    def get_contract_clients(self) -> dict:
        """
        Get contract clients to retrieve clientIds and details.
        """
        return self._post("client/contract/", {})

    def find_country(self, name: str = None, iso_alpha2: str = None) -> dict:
        """
        Find country info by name (full/partial) or ISO Alpha-2 code.
        """
        data = {}
        if name:
            data["name"] = name
        if iso_alpha2:
            data["isoAlpha2"] = iso_alpha2
        return self._post("location/country/", data)

    def find_state(self, country_id: int, name: str) -> dict:
        """
        Find a state using country ID and name (or partial).
        """
        return self._post("location/state/", {"countryId": country_id, "name": name})

    def find_office(
        self, country_id: int = None, site_id: int = None, name: str = None
    ) -> dict:
        """
        Locate offices by country, site, or partial name.
        """
        data = {}
        if country_id is not None:
            data["countryId"] = country_id
        if site_id is not None:
            data["siteId"] = site_id
        if name:
            data["name"] = name
        return self._post("location/office/", data)

    def find_site(
        self,
        country_id: int,
        name: str = None,
        post_code: str = None,
        site_type: str = None,
        region: str = None,
    ) -> dict:
        """
        Search sites with combinations to narrow results.
        """
        data = {"countryId": country_id}
        if name:
            data["name"] = name
        if post_code:
            data["postCode"] = post_code
        if site_type:
            data["type"] = site_type
        if region:
            data["region"] = region
        return self._post("location/site/", data)

    def find_complex(self, site_id: int, name: str) -> dict:
        """
        Get complex info based on site and partial name.
        """
        return self._post("location/complex/", {"siteId": site_id, "name": name})

    def find_street(self, site_id: int, name: str, street_type: str = None) -> dict:
        """
        Locate streets by name and optional type (e.g. 'bul.').
        """
        data = {"siteId": site_id, "name": name}
        if street_type:
            data["type"] = street_type
        return self._post("location/street/", data)

    def find_poi(self, site_id: int, name: str) -> dict:
        """
        Get points of interest (POIs) by name in a given site.
        """
        return self._post("location/poi/", {"siteId": site_id, "name": name})

    def destination_services(
        self, sender_client_id: int = None, recipient: dict = None, date: str = None
    ) -> dict:
        """
        Get available services between sender and recipient (privatePerson + addressLocation).
        """
        data = {}
        if date:
            data["date"] = date
        if sender_client_id is not None:
            data["sender"] = {"clientId": sender_client_id}
        if recipient:
            data["recipient"] = recipient
        return self._post("services/destination", data)

    def calculate(self, sender: dict, recipient: dict) -> dict:
        """
        Calculate service cost using sender (address or office) and recipient.
        """
        return self._post(
            "services/destination", {"sender": sender, "recipient": recipient}
        )
