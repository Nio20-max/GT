# Formula Discovery Report

Date: 2026-03-05
Scope: Training progression baseline calibration for launch.

## Method

- Implemented deterministic training model in `backend/app/domain/training.py` using deep-spec anchors:
  - Talent factor: `0.85 + 0.03 * talent`.
  - Style multipliers: conservative `0.88`, balanced `1.00`, aggressive `1.14`.
  - Age multipliers and 30+ decay from `plan/10_training_system_deep_spec.md`.
  - High-strength damping for `strength > 700`: `exp(-(strength-700)/220)`.
- Ran unit tests (`pytest`) to validate boundaries and damping behavior.
- Ran empirical scenarios via `backend/scripts/formula_discovery.py` to choose conservative launch base gains.

## Selected Baseline Constants

- `BASE_GAIN_BY_SKILL`
  - goalkeeper: `1.30`
  - defense: `1.22`
  - midfield: `1.18`
  - attack: `1.15`
- Fatigue model:
  - `fatigue_factor = max(0.55, 1.0 - 0.0045 * fatigue)` where `fatigue in [0,100]`.
  - Interpretation: max training penalty from fatigue is 45%.
- Injury interaction:
  - Deferred to simulation phase for market-wide balancing; training-style multipliers already model risk-reward pressure.

## Empirical Outputs

Measured scenario outputs from script run:

1. `{age: 18, strength: 120, talent: 8, style: balanced, bucket: midfield, fatigue: 10} -> daily_gain: 1.4249`
2. `{age: 22, strength: 300, talent: 7, style: aggressive, bucket: attack, fatigue: 15} -> daily_gain: 1.3736`
3. `{age: 25, strength: 550, talent: 6, style: balanced, bucket: defense, fatigue: 25} -> daily_gain: 1.1152`
4. `{age: 29, strength: 680, talent: 5, style: conservative, bucket: goalkeeper, fatigue: 35} -> daily_gain: 0.8674`
5. `{age: 31, strength: 760, talent: 6, style: balanced, bucket: midfield, fatigue: 45} -> daily_gain: 0.4018`
6. `{age: 34, strength: 900, talent: 4, style: conservative, bucket: defense, fatigue: 70} -> daily_gain: 0.0000`

## Acceptance Criteria Validation

- Gain is positive for youth/prime players under moderate fatigue.
- Gain declines smoothly with age and high strength.
- Age 34 high-strength players can naturally plateau at or near zero gain.
- No negative gain is returned by training function.

## Recommended Parameter Ranges For Future Tuning

- Base gains by skill bucket: `1.10 - 1.40`.
- Fatigue slope: `0.0035 - 0.0050` per fatigue point.
- Fatigue floor factor: `0.50 - 0.65`.
- High-strength damping denominator: `200 - 260` (current `220`).

## Follow-up In Phase C/F

- Use multi-season simulations to calibrate progression half-life toward target `strength` distributions.
- Add explicit injury probability function once health subsystem is implemented.
- Re-balance base gains if transfer market and league parity diverge.
