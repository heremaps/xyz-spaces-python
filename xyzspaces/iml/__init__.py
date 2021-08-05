"""This module defines ``IML`` class to interact with Interactive Map Layer."""

import logging
import time
from typing import Any, Dict, Optional

from xyzspaces.iml.apis.aaa_oauth2_api import AAAOauth2Api
from xyzspaces.iml.apis.data_config_api import DataConfigApi
from xyzspaces.iml.auth import Auth
from xyzspaces.iml.catalog import Catalog
from xyzspaces.iml.credentials import Credentials
from xyzspaces.iml.layer import InteractiveMapLayer

logger = logging.getLogger(__name__)


class IML:
    """A single interface to interact with Interactive Map Layer."""

    def __init__(self):
        self.catalog = None
        self.layer = None

    @classmethod
    def from_catalog_hrn_and_layer_id(
        cls, catalog_hrn: str, layer_id: str, credentials: Optional[Credentials] = None
    ) -> "IML":
        """Instantiate a IML object for an existing catalog and interactive map layer.

        :param catalog_hrn: HRN of the catalog.
        :param layer_id: a string with the layer ID of this layer.
        :param credentials: object of :class:`Credentials`.
        :return: Object of IML
        """
        obj = cls()
        cred = credentials or Credentials.from_default()
        catalog = Catalog(hrn=catalog_hrn, credentials=cred)
        obj.catalog = catalog
        obj.layer = InteractiveMapLayer(layer_id=layer_id, catalog=catalog)
        return obj

    @classmethod
    def new(
        cls,
        catalog_id: str,
        catalog_name: str,
        catalog_summary: str,
        catalog_description: str,
        layer_details: Dict,
        credentials: Optional[Credentials] = None,
        billing_tag: Optional[str] = None,
        proxies: Optional[Dict] = None,
    ) -> "IML":
        """
        Create a new catalog and interactive map layer.

        :param catalog_id: ID of the catalog.
        :param catalog_name: name of the catalog.
        :param catalog_summary: catalog summary.
        :param catalog_description: catalog description.
        :param layer_details: A dict to represent interactive map layer details.
        :param credentials: A Credentials instance.
        :param billing_tag: A string to represent billing tag.
        :param proxies: A dict to represnt proxies.
        :return: Object of IML.
        """
        data: Dict[str, Any] = dict(layers=[layer_details])
        data["id"] = catalog_id
        data["name"] = catalog_name
        data["summary"] = catalog_summary
        data["description"] = catalog_description

        cred = credentials or Credentials.from_default()
        aaa_oauth2_api = AAAOauth2Api(
            base_url=cred.cred_properties["endpoint"], proxies={}
        )
        auth = Auth(credentials=cred, aaa_oauth2_api=aaa_oauth2_api)
        data_config_api = DataConfigApi(auth=auth, proxies=proxies)
        response = data_config_api.create_catalog(data=data, billing_tag=billing_tag)
        status_response, complete = data_config_api.get_catalog_status(
            response["href"], billing_tag
        )
        while not complete:
            time.sleep(5)
            status_response, complete = data_config_api.get_catalog_status(
                response["href"], billing_tag
            )
        obj = cls()
        obj.catalog = Catalog(hrn=status_response["hrn"], credentials=cred)
        cat_details = obj.catalog.get_details()
        lyr_details = {lr["id"]: lr for lr in cat_details["layers"]}
        assert layer_details["id"] in lyr_details, "provided layer_id is not created."
        obj.layer = InteractiveMapLayer(layer_id=layer_details["id"], catalog=obj.catalog)
        return obj

    def add_interactive_map_layer(
        self,
        catalog_hrn: str,
        layer_details: Dict,
        credentials: Optional[Credentials] = None,
        billing_tag: Optional[str] = None,
        proxies: Optional[Dict] = None,
    ) -> None:
        """Add a new interactive map layer to existing catalog.

        :param catalog_hrn: HRN of the catalog.
        :param layer_details: A dict to represent interactive map layer details.
        :param credentials: A Credentials instance.
        :param billing_tag: A string to represent billing tag.
        :param proxies: A dict to represnt proxies.
        """
        cred = credentials or Credentials.from_default()
        self.catalog = Catalog(hrn=catalog_hrn, credentials=cred)
        catalog_details = self.catalog.get_details()
        existing_layers = catalog_details.get("layers", [])
        existing_layers.append(layer_details)
        data: Dict[str, Any] = dict(layers=existing_layers)
        data["id"] = catalog_details["id"]
        data["name"] = catalog_details["name"]
        data["summary"] = catalog_details["summary"]
        data["description"] = catalog_details["description"]

        aaa_oauth2_api = AAAOauth2Api(
            base_url=cred.cred_properties["endpoint"], proxies={}
        )
        auth = Auth(credentials=cred, aaa_oauth2_api=aaa_oauth2_api)
        data_config_api = DataConfigApi(auth=auth, proxies=proxies)
        response = data_config_api.update_catalog(
            catalog_hrn=catalog_hrn, data=data, billing_tag=billing_tag
        )
        status_response, complete = data_config_api.get_catalog_status(
            response["href"], billing_tag=billing_tag
        )
        while not complete:
            time.sleep(5)
            status_response, complete = data_config_api.get_catalog_status(
                response["href"], billing_tag=billing_tag
            )
        self.layer = InteractiveMapLayer(
            layer_id=layer_details["id"], catalog=self.catalog
        )

    def delete_catalog(
        self,
        catalog_hrn: str,
        credentials: Optional[Credentials] = None,
        billing_tag: Optional[str] = None,
        proxies: Optional[Dict] = None,
    ) -> None:
        """
        Delete a catalog along with the layers it contains.

        :param catalog_hrn: The *HERE Resource Name* of the catalog
        :param credentials: The credentials object.
        :param billing_tag: A string to represent billing tag.
        :param proxies: A dict to represnt proxies.
        """
        cred = credentials or Credentials.from_default()
        aaa_oauth2_api = AAAOauth2Api(
            base_url=cred.cred_properties["endpoint"], proxies={}
        )
        auth = Auth(credentials=cred, aaa_oauth2_api=aaa_oauth2_api)
        data_config_api = DataConfigApi(auth=auth, proxies=proxies)
        response = data_config_api.delete_catalog(catalog_hrn, billing_tag)
        while True:
            time.sleep(5)
            status_response, complete = data_config_api.get_catalog_status(
                response["href"], billing_tag=billing_tag
            )
            status = status_response["status"]
            logger.debug(f"Catalog delete: {catalog_hrn} state: {status}")
            if complete:
                logger.info(
                    f"Catalog deletion for hrn: {catalog_hrn} finished with status: "
                    f"{status} "
                )
                self.catalog = None
                self.layer = None
                return
