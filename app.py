#!/usr/bin/env python3
import os

import aws_cdk as cdk

from knowlio.knowlio_stack import KnowlioStack


app = cdk.App()
KnowlioStack(app, "KnowlioStack",
    env=cdk.Environment(account='891377379904', region='us-east-1'),
    )

app.synth()