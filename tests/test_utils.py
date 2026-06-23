import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from entities.ball import Ball
from utils.utils import (
    calc_importance_factor,
    calc_intent,
    calc_mass_center,
    calc_normal,
    orbit_target,
    team_mass_ratio,
    team_tactic,
)


class _Blob:
    def __init__(self, mass):
        self.mass = mass


def _ball(mass, team, pos=(0, 0)):
    return Ball(pos, config.COLOR_BLUE if team == config.TEAM_BLUE else config.COLOR_RED, mass, team)


def test_calc_normal_unit_vector():
    dist, normal = calc_normal((0, 0), (3, 4))
    assert dist == pytest.approx(5.0)
    assert normal == pytest.approx((0.6, 0.8))


def test_calc_normal_zero_distance():
    dist, normal = calc_normal((1, 1), (1, 1))
    assert dist == 0
    assert normal == (0, 0)


def test_calc_intent_flees_larger_enemy():
    ball = _ball(100, config.TEAM_BLUE)
    enemy = _ball(400, config.TEAM_RED, (10, 0))
    assert calc_intent(ball, enemy, 0, 0) < 0


def test_calc_intent_chases_smaller_enemy():
    ball = _ball(400, config.TEAM_BLUE)
    enemy = _ball(100, config.TEAM_RED, (10, 0))
    assert calc_intent(ball, enemy, 0, 0) > 0


def test_team_tactic_thresholds():
    assert team_tactic(1.5) == "defense"
    assert team_tactic(1.0) == "neutral"
    assert team_tactic(0.5) == "attack"


def test_team_mass_ratio():
    own = _Blob(600)
    enemy = _Blob(400)
    assert team_mass_ratio(own, enemy) == pytest.approx(1.5)
    assert team_mass_ratio(None, enemy) == 1.0


def test_calc_importance_factor_clamped():
    assert calc_importance_factor(0, 10) == 0
    assert calc_importance_factor(1, 10) == pytest.approx(10 / 11)
    assert calc_importance_factor(100, 10) < 0.1


def test_orbit_target_on_ring():
    target = orbit_target((50, 0), (0, 0), 10, orbit_factor=2.0)
    assert target[0] == pytest.approx(20.0)
    assert target[1] == pytest.approx(0.0)


def test_calc_mass_center():
    balls = [_ball(100, config.TEAM_BLUE, (0, 0)), _ball(300, config.TEAM_BLUE, (10, 0))]
    center = calc_mass_center(balls)
    assert center == pytest.approx((7.5, 0.0))
