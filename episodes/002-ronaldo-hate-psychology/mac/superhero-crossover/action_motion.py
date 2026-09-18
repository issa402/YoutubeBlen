"""Deterministic overhead ankle throw in the camera's X/Z plane.

Coordinates are world units. Angles use Blender's positive Y rotation:
``x' = cos(a)*x + sin(a)*z`` and ``z' = -sin(a)*x + cos(a)*z``.
The ankle landmark is calibrated for the five-unit-high action-tumble sprite.
This module performs no rendering and has no Blender dependency.
"""
from dataclasses import dataclass
import math

ANKLE = (-0.05, -1.55)
ARM_LENGTH = 1.4
RELEASE_FRAME = 11
SHOULDER = (-1.4, 1.25)
REACH = 2.76
HOLD_ANGLE = 2.37
RELEASE_ANGLE = 0.75
VICTIM_RELEASE_ANGLE = 1.55
GRAVITY = 0.12  # World units per frame squared, deliberately stylized.


@dataclass(frozen=True)
class ThrowPose:
    shoulder: tuple[float, float]
    elbow: tuple[float, float]
    grip: tuple[float, float]
    center: tuple[float, float]
    angle: float
    scale: float
    held: bool


def transform_point(point, center, angle, scale=1.0):
    """Project a local sprite landmark using Blender's Y rotation convention."""
    x, z = point
    cosine, sine = math.cos(angle), math.sin(angle)
    return (center[0] + scale * (cosine * x + sine * z),
            center[1] + scale * (-sine * x + cosine * z))


def _grip(angle):
    return (SHOULDER[0] + REACH * math.cos(angle),
            SHOULDER[1] + REACH * math.sin(angle))


def _elbow(grip):
    """Two-circle intersection keeps both arm segments exactly 1.4 units."""
    dx, dz = grip[0] - SHOULDER[0], grip[1] - SHOULDER[1]
    span = math.hypot(dx, dz)
    bend = math.sqrt(ARM_LENGTH ** 2 - (span * 0.5) ** 2)
    return (SHOULDER[0] + dx * 0.5 - dz / span * bend,
            SHOULDER[1] + dz * 0.5 + dx / span * bend)


def _held_pose(frame):
    progress = max(0.0, (frame - 5) / 6)
    swing = progress ** 2  # Accelerate continuously into release.
    grip_angle = HOLD_ANGLE + (RELEASE_ANGLE - HOLD_ANGLE) * swing
    victim_angle = math.pi + (VICTIM_RELEASE_ANGLE - math.pi) * swing
    grip = _grip(grip_angle)
    ankle_offset = transform_point(ANKLE, (0.0, 0.0), victim_angle)
    center = (grip[0] - ankle_offset[0], grip[1] - ankle_offset[1])
    return grip, center, victim_angle


def _release_velocity():
    """Analytic derivative avoids a position or speed pop at the release cut."""
    grip_rate = (RELEASE_ANGLE - HOLD_ANGLE) / 3
    victim_rate = (VICTIM_RELEASE_ANGLE - math.pi) / 3
    grip_vx = -REACH * math.sin(RELEASE_ANGLE) * grip_rate
    grip_vz = REACH * math.cos(RELEASE_ANGLE) * grip_rate
    x, z = ANKLE
    angle = VICTIM_RELEASE_ANGLE
    ankle_vx = (-math.sin(angle) * x + math.cos(angle) * z) * victim_rate
    ankle_vz = (-math.cos(angle) * x - math.sin(angle) * z) * victim_rate
    return (grip_vx - ankle_vx, grip_vz - ankle_vz), victim_rate


def throw_pose(frame):
    """Return hold (1–5), swing (6–10), and free flight (11+) poses.

    The victim's ankle is exactly attached to the grip before frame 11.
    At release, center position and velocity remain continuous. The hand then
    follows through while the victim flies right, falls, and grows toward camera.
    Fractional frames are supported for motion inspection and future subframes.
    """
    if isinstance(frame, bool) or not isinstance(frame, (int, float)) or not math.isfinite(frame) or frame < 1:
        raise ValueError('frame must be a finite number greater than or equal to 1')
    if frame < RELEASE_FRAME:
        grip, center, angle = _held_pose(frame)
        return ThrowPose(SHOULDER, _elbow(grip), grip, center, angle, 1.0, True)

    dt = frame - RELEASE_FRAME
    _, release_center, release_angle = _held_pose(RELEASE_FRAME)
    velocity, angular_velocity = _release_velocity()
    center = (release_center[0] + velocity[0] * dt,
              release_center[1] + velocity[1] * dt - 0.5 * GRAVITY * dt * dt)
    follow = min(1.0, dt / 2)
    follow = follow * follow * (3 - 2 * follow)
    grip = _grip(RELEASE_ANGLE - 0.6 * follow)
    return ThrowPose(SHOULDER, _elbow(grip), grip, center,
                     release_angle + angular_velocity * dt,
                     1.0 + 0.07 * min(dt, 3), False)
