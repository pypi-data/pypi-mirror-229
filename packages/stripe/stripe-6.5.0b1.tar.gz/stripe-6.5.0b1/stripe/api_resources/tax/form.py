# -*- coding: utf-8 -*-
# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

import stripe
from stripe import api_requestor, util
from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.expandable_field import ExpandableField
from stripe.stripe_object import StripeObject
from typing import List
from typing import Optional
from typing_extensions import Literal
from urllib.parse import quote_plus


class Form(ListableAPIResource["Form"]):
    """
    Tax forms are legal documents which are delivered to one or more tax authorities for information reporting purposes.

    Related guide: [US tax reporting for Connect platforms](https://stripe.com/docs/connect/tax-reporting)
    """

    OBJECT_NAME = "tax.form"
    corrected_by: Optional[ExpandableField["Form"]]
    created: str
    filing_statuses: List[StripeObject]
    id: str
    livemode: bool
    object: Literal["tax.form"]
    payee: StripeObject
    type: str
    us_1099_k: StripeObject
    us_1099_misc: StripeObject
    us_1099_nec: StripeObject

    @classmethod
    def _cls_pdf(
        cls,
        sid,
        api_key=None,
        idempotency_key=None,
        stripe_version=None,
        stripe_account=None,
        **params
    ):
        url = "%s/%s/%s" % (
            cls.class_url(),
            quote_plus(sid),
            "pdf",
        )
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=stripe.upload_api_base,
            api_version=stripe_version,
            account=stripe_account,
        )
        headers = util.populate_headers(idempotency_key)
        response, _ = requestor.request_stream("get", url, params, headers)
        return response

    @util.class_method_variant("_cls_pdf")
    def pdf(
        self,
        api_key=None,
        api_version=None,
        stripe_version=None,
        stripe_account=None,
        **params
    ):
        version = api_version or stripe_version
        requestor = api_requestor.APIRequestor(
            api_key,
            api_base=stripe.upload_api_base,
            api_version=version,
            account=stripe_account,
        )
        url = self.instance_url() + "/pdf"
        return requestor.request_stream("get", url, params=params)
