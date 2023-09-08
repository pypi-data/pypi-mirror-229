import requests

from spackle import log
from spackle.exceptions import SpackleException


class PricingTable:
    @staticmethod
    def retrieve(pricing_table_id):
        from spackle import api_key, api_base

        response = requests.get(
            f"{api_base}/pricing_Tables/{pricing_table_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
        )

        if response.status_code != 200:
            raise SpackleException(
                "Pricing table %s not found; status code: %s; response: %s"
                % (pricing_table_id, response.status_code, response.text)
            )

        data = response.json()
        log.log_debug(
            "Retrieved pricing table data for %s: %s" % (pricing_table_id, data)
        )
        return data
