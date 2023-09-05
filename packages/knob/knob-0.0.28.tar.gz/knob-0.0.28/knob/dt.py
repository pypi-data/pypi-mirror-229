# -*- coding:utf-8 -*-

__all__ = ['local_now', 'local_today', 'local_time']

import six
from django.utils import timezone
from dt_utils import T


def local_now():
    return timezone.now().astimezone(timezone.get_default_timezone())


def local_today():
    return local_now().date()


def local_time(raw_time):
    py_time = T(raw_time)
    if timezone.is_aware(py_time):
        return py_time
    else:
        return timezone.make_aware(py_time, timezone=timezone.get_default_timezone())

