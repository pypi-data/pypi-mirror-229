# -*- coding: utf-8 -*-
# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from stripe.api_resources.abstract import ListableAPIResource
from typing_extensions import Literal


class CardBundle(ListableAPIResource["CardBundle"]):
    """
    A Card Bundle represents the bundle of physical items - card stock, carrier letter, and envelope - that is shipped to a cardholder when you create a physical card.
    """

    OBJECT_NAME = "issuing.card_bundle"
    id: str
    livemode: bool
    name: str
    object: Literal["issuing.card_bundle"]
    status: str
    type: str
