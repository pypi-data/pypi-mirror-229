# -*- coding: utf-8 -*-
# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from stripe import util
from stripe.api_resources.abstract import APIResourceTestHelpers
from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.expandable_field import ExpandableField
from typing import Dict
from typing import Optional
from typing_extensions import Literal
from typing_extensions import Type

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from stripe.api_resources.issuing.card_bundle import CardBundle


class CardDesign(
    ListableAPIResource["CardDesign"],
    UpdateableAPIResource["CardDesign"],
):
    """
    A Card Design is a logical grouping of a Card Bundle, card logo, and carrier text that represents a product line.
    """

    OBJECT_NAME = "issuing.card_design"
    card_bundle: ExpandableField["CardBundle"]
    id: str
    lookup_key: Optional[str]
    metadata: Dict[str, str]
    name: Optional[str]
    object: Literal["issuing.card_design"]
    preference: str
    status: str

    class TestHelpers(APIResourceTestHelpers["CardDesign"]):
        _resource_cls: Type["CardDesign"]

        @classmethod
        def _cls_activate_testmode(
            cls,
            card_design,
            api_key=None,
            stripe_version=None,
            stripe_account=None,
            **params
        ):
            return cls._static_request(
                "post",
                "/v1/test_helpers/issuing/card_designs/{card_design}/status/activate".format(
                    card_design=util.sanitize_id(card_design)
                ),
                api_key=api_key,
                stripe_version=stripe_version,
                stripe_account=stripe_account,
                params=params,
            )

        @util.class_method_variant("_cls_activate_testmode")
        def activate_testmode(self, idempotency_key=None, **params):
            return self.resource._request(
                "post",
                "/v1/test_helpers/issuing/card_designs/{card_design}/status/activate".format(
                    card_design=util.sanitize_id(self.resource.get("id"))
                ),
                idempotency_key=idempotency_key,
                params=params,
            )

        @classmethod
        def _cls_deactivate_testmode(
            cls,
            card_design,
            api_key=None,
            stripe_version=None,
            stripe_account=None,
            **params
        ):
            return cls._static_request(
                "post",
                "/v1/test_helpers/issuing/card_designs/{card_design}/status/deactivate".format(
                    card_design=util.sanitize_id(card_design)
                ),
                api_key=api_key,
                stripe_version=stripe_version,
                stripe_account=stripe_account,
                params=params,
            )

        @util.class_method_variant("_cls_deactivate_testmode")
        def deactivate_testmode(self, idempotency_key=None, **params):
            return self.resource._request(
                "post",
                "/v1/test_helpers/issuing/card_designs/{card_design}/status/deactivate".format(
                    card_design=util.sanitize_id(self.resource.get("id"))
                ),
                idempotency_key=idempotency_key,
                params=params,
            )

    @property
    def test_helpers(self):
        return self.TestHelpers(self)


CardDesign.TestHelpers._resource_cls = CardDesign
