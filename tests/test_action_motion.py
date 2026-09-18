"""Physical contracts for the overhead throw, independent of Blender."""
import math

import pytest

from blender.action_motion import ANKLE, ARM_LENGTH, RELEASE_FRAME, throw_pose, transform_point


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def test_held_ankle_stays_in_the_hand_through_the_swing():
    for frame in range(1, RELEASE_FRAME):
        pose = throw_pose(frame)
        assert pose.held
        assert distance(transform_point(ANKLE, pose.center, pose.angle, pose.scale), pose.grip) < 1e-10


def test_arm_segments_keep_their_lengths_and_form_a_connected_chain():
    for frame in range(1, 14):
        pose = throw_pose(frame)
        assert distance(pose.shoulder, pose.elbow) == pytest.approx(ARM_LENGTH)
        assert distance(pose.elbow, pose.grip) == pytest.approx(ARM_LENGTH)


def test_opening_is_upside_down_then_swings_from_left_to_right():
    opening, release = throw_pose(1), throw_pose(RELEASE_FRAME)
    assert opening.angle == pytest.approx(math.pi)
    assert opening.grip[0] < opening.shoulder[0]
    assert release.grip[0] > release.shoulder[0]
    assert release.center[0] > opening.center[0] + 4
    assert not release.held


def test_release_position_and_velocity_are_continuous():
    epsilon = 1e-5
    before, release, after = (throw_pose(RELEASE_FRAME + d) for d in (-epsilon, 0, epsilon))
    assert distance(before.center, release.center) < 1e-4
    assert distance(after.center, release.center) < 1e-4
    incoming = tuple((b - a) / epsilon for a, b in zip(before.center, release.center))
    outgoing = tuple((b - a) / epsilon for a, b in zip(release.center, after.center))
    assert incoming == pytest.approx(outgoing, abs=1e-4)


def test_victim_separates_after_release_and_keeps_travelling_right():
    poses = [throw_pose(frame) for frame in (11, 12, 13)]
    assert all(not pose.held for pose in poses)
    assert poses[0].center[0] < poses[1].center[0] < poses[2].center[0]
    assert poses[0].scale < poses[1].scale < poses[2].scale
    assert distance(transform_point(ANKLE, poses[-1].center, poses[-1].angle, poses[-1].scale), poses[-1].grip) > 1


@pytest.mark.parametrize('frame', [0, -1, float('inf'), float('nan'), True, '1'])
def test_invalid_frame_fails_with_a_clear_error(frame):
    with pytest.raises(ValueError, match='frame'):
        throw_pose(frame)
