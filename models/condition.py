import datetime

from django.db import models
from django.utils import timezone
import pytz

import app.utils as utils
import tbt_helpers.models as tbt_models
from rules_engine.models.rule import Rule
from rules_engine.exceptions import RuleEngineException

class Condition(tbt_models.TBTBaseModel):

    RULE_TYPE_AND = "And"
    RULE_TYPE_OR = "Or"
    RULE_TYPES = (
        (RULE_TYPE_AND, "AND"),
        (RULE_TYPE_OR, "OR"),
    )

    OPERATOR_TYPE_GREATER = ">"
    OPERATOR_TYPE_LESSER = "<"
    OPERATOR_TYPE_EQUALS = "=="
    OPERATOR_TYPES = (
        (OPERATOR_TYPE_GREATER, "GREATER THAN"),
        (OPERATOR_TYPE_LESSER, "LESSER THAN"),
        (OPERATOR_TYPE_EQUALS, "EQUALS"),
    )

    CONTENT_TYPE_STRING = "String"
    CONTENT_TYPE_NUMBER = "Number"
    CONTENT_TYPE_BOOLEAN = "Boolean"
    CONTENT_TYPE_DATE = "Date"
    CONTENT_TYPES = (
        (CONTENT_TYPE_STRING, "String"),
        (CONTENT_TYPE_NUMBER, "Number"),
        (CONTENT_TYPE_BOOLEAN, "Boolean"),
        (CONTENT_TYPE_DATE, "Date"),
    )

    type = models.CharField(max_length=12, choices=RULE_TYPES,
            default=RULE_TYPE_AND)
    field = models.CharField(max_length=64)
    value = models.CharField(max_length=128)
    content_type = models.CharField(max_length=32, choices=CONTENT_TYPES,
            default=CONTENT_TYPE_STRING)
    operator = models.CharField(max_length=12, choices=OPERATOR_TYPES,
            default=OPERATOR_TYPE_EQUALS)
    rule = models.ForeignKey(Rule, related_name="conditions", null=False,
            on_delete=models.CASCADE)

    """
    All comparison values are stored in the database as strings.

    The content_type field is used to help us (de)serialize these string
    into the appropriate value.

    To avoid confusion, assumption will be that all dates are "datetimes".
    """

    def _evaluate(self, value, data):
        if self.operator == self.OPERATOR_TYPE_GREATER:
            return data > value
        elif self.operator == self.OPERATOR_TYPE_LESSER:
            return data < value
        else:
            return data == value

    def evaluate_string(self, data):
        """
        Self's value is a string.
        """
        # TODO: Remove after python3 migration; remove lines 74-78
        try:
            if isinstance(data, unicode):
                data = str(data)
        except NameError:
            pass

        # error if we don't have a string
        if not isinstance(data, str):
            raise RuleEngineException(str(data.__class__) + " is expected to be a string.")

        value = str(self.value)
        return self._evaluate(value, data)

    def evaluate_number(self, data):
        """
        Self's value is numeric.  We compare them as floats.
        """
        if not is_number(data):
            raise RuleEngineException(str(data.__class__) + " is expected to be a number.")

        data = float(data)
        value = float(self.value)

        return self._evaluate(value, data)

    def evaluate_boolean(self, data):
        try:
            data = utils.parse_boolean(data)
            value = utils.parse_boolean(self.value)
            return self._evaluate(value, data)
        except TypeError:
            raise RuleEngineException(str(data.__class__) + " is expected to be a boolean.")

    def evaluate_date(self, data):
        """
        Convert to datetimes and then compare.
        """
        if isinstance(data, datetime.date) and not isinstance(data, datetime.datetime):
            data = datetime.datetime.combine(data, datetime.datetime.min.time())

        if not isinstance(data, datetime.datetime):
            raise RuleEngineException(str(data.__class__) + " is expected to be a date.")

        value = timezone.make_aware(string_to_date(self.value), timezone=pytz.timezone('UTC'))
        return self._evaluate(value, data)

    def evaluate(self, an_object):
        """
        Compare object type
        """
        if not isinstance(an_object, self.rule.model.model_class()):
            raise RuleEngineException("Bad rule content type")

        data = getattr(an_object, self.field)

        if self.content_type == self.CONTENT_TYPE_STRING:
            return self.evaluate_string(data)
        elif self.content_type == self.CONTENT_TYPE_NUMBER:
            return self.evaluate_number(data)
        elif self.content_type == self.CONTENT_TYPE_BOOLEAN:
            return self.evaluate_boolean(data)
        elif self.content_type == self.CONTENT_TYPE_DATE:
            return self.evaluate_date(data)
        else:
            raise RuleEngineException("Bad rule content type")

DEFAULT_DATETIME_FORMAT = '%c %f'

def date_to_string(date):
    if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
        date_as_datetime = datetime.datetime.combine(date, datetime.datetime.min.time())
        return date_as_datetime.strftime(DEFAULT_DATETIME_FORMAT)
    elif isinstance(date, datetime.datetime):
        return date.strftime(DEFAULT_DATETIME_FORMAT)
    else:
        raise RuleEngineException(str(date.__class__) + " is expected to be a date.")

def string_to_date(date_string):
    """
    Returns a datetime.  Caller is responsible to convert to date, etc.
    """
    return datetime.datetime.strptime(date_string, DEFAULT_DATETIME_FORMAT)

def is_number(s):
    try:
        i = float(s)
    except (ValueError, TypeError):
        return False
    return True
