# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.documentviewer.async import JobRunner
from collective.documentviewer.convert import Converter
from imio.annex.events import ConversionStartedEvent
from zope.event import notify


def converter_call(self, *args, **kwargs):
    notify(ConversionStartedEvent(self.context))
    return Converter._old___call__(self, *args, **kwargs)


def jobrunner_queue_it(self):
    JobRunner._old_queue_it(self)
    notify(ConversionStartedEvent(self.object))
