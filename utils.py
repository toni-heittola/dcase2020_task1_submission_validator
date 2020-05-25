#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Toni Heittola ( toni.heittola@tuni.fi ), Tampere University / Audio Research Group
# License: MIT


def is_float(value):
    """Check if given value is float

    Copied from dcase_util/utils.py

    Parameters
    ----------
    value : variable

    Returns
    -------
    bool

    """

    if value is not None:
        try:
            float(value)
            return True

        except ValueError:
            return False

    else:
        return False


def is_int(value):
    """Check if given value is integer

    Copied from dcase_util/utils.py

    Parameters
    ----------
    value : variable

    Returns
    -------
    bool

    """

    if value is not None:
        try:
            int(value)
            return True

        except ValueError:
            return False

    else:
        return False


def check_fields(source, target):
    if isinstance(source, dict):
        return len(set(list(source.keys())) & set(target)) != len(target)

    elif isinstance(source, list):
        return len(set(source) & set(target)) != len(target)

