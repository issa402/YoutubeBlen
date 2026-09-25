"""Blender 5 removed Action.fcurves; layered actions must still animate."""
from types import SimpleNamespace as NS

from blender.animation_compat import iter_action_curves


def test_layered_action_without_legacy_fcurves():
    first, second = object(), object()
    action = NS(layers=[NS(strips=[NS(channelbags=[NS(fcurves=[first])]),
                                 NS(channelbags=[NS(fcurves=[second])])])])
    assert list(iter_action_curves(action)) == [first, second]


def test_legacy_action_and_empty_action():
    curve = object()
    assert list(iter_action_curves(NS(layers=[], fcurves=[curve]))) == [curve]
    assert list(iter_action_curves(NS(layers=[]))) == []


def test_layered_action_does_not_double_read_legacy_alias():
    curve = object()
    action = NS(layers=[NS(strips=[NS(channelbags=[NS(fcurves=[curve])])])],
                fcurves=[curve])
    assert list(iter_action_curves(action)) == [curve]
