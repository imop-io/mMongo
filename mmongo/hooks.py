# coding: utf8

import logging

from .fields import Null
from .errors import ColumnIsRequired

logger = logging.getLogger(__name__)


def validate_columns_before_save(*args):
    _, (model, *_), _ = args
    for column, typo in model.__mapping__.items():
        if column not in model:
            if typo.required is True:
                if isinstance(typo.default, Null):
                    raise ColumnIsRequired(column, model)
                else:
                    default = (callable(typo.default) and typo.default()) \
                        or typo.default
                    model[column] = default
            else:
                if not isinstance(typo.default, Null):
                    model[column] = typo.default
        else:
            if not typo.validate(model[column]):
                raise TypeError(
                    "Column<{}> of {} must be {}, but {}<{}> found!".format(
                        column,
                        model.__class__.__name__,
                        [t.__name__ for t in typo.types],
                        type(model[column]).__name__,
                        repr(model[column])
                    )
                )


def log_modified_after_save(*args):
    logger.debug('after save %s', args)
