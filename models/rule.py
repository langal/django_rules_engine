import json
import ast
import datetime
import logging
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

import tbt_helpers.models as tbt_models
from app.models.core import nullable
from rules_engine.exceptions import RuleEngineException

logger = logging.getLogger(__name__)

class Rule(tbt_models.TBTBaseModel):

    name = models.CharField(max_length=64)
    model = models.ForeignKey(ContentType, related_name="rule_conditions", null=False,
            on_delete=models.CASCADE)
    tag = models.CharField(max_length=64, **nullable)
    halt = models.BooleanField(default=False, verbose_name="Stop Further Rules")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    expiration = models.DateField(**nullable)

    # the action maps to a function that will be executed on the applied object
    # the action_args (key/value) will be passed in as a **kwargs
    action = models.CharField(max_length=64, **nullable)
    action_args = models.CharField(max_length=128, **nullable)

    def evaluate(self, an_object):
        for condition in self.conditions.all():
            if not condition.evaluate(an_object):
                return False
        return True

    def execute(self, an_object):
        func = getattr(an_object, self.action, None)
        if func is None:
            raise RuleEngineException(self.action + " is not a function of " + an_object.__class)
        else:
            literal_args = ast.literal_eval(self.action_args)
            if isinstance(literal_args, dict):
                an_object = func(**literal_args)
            else:
                arguments = json.loads(literal_args)
                an_object = func(**arguments)
        return an_object


"""
Self for all rules by TAG and apply them to an object
"""
def apply_all_rules(rule_tag, an_object):
    try:
        rules = Rule.objects.filter(tag=rule_tag).filter(Q(is_active=True) & \
            (Q(expiration__gt=datetime.datetime.now()) | \
            Q(expiration=None))) \
            .order_by('priority')
        for rule in rules.all():
            if rule.evaluate(an_object):
                rule.execute(an_object)
                if rule.halt:
                    break
    except Exception as e:
        """
        We do not want Exception to block
        here.  Since we do not know deterministically
        what is being called, we cannot know
        what to catch
        """
        logger.exception(e)
    return an_object

PRE_SHIPPING_RULES = "PRE_SHIPPING" # operates on ORDERS
