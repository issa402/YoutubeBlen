"""Action traversal shared by Blender 4.5 and 5.x, without importing bpy."""


def iter_action_curves(action):
    """Visit each slot's curves; Blender 5 has no legacy Action.fcurves."""
    layers = getattr(action, "layers", ())
    if layers:
        for layer in layers:
            for strip in layer.strips:
                for channelbag in getattr(strip, "channelbags", ()):
                    yield from channelbag.fcurves
    else:
        yield from getattr(action, "fcurves", ())
