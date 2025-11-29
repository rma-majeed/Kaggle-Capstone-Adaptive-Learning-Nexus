"""
Curriculum Optimizer Loop Sub-Agents Package

Contains agents for iterative curriculum optimization:
- CurriculumGenerator: Creates curriculum plans
- PlanValidator: Validates and approves plans
"""

from .curriculum_generator.agent import (
    create_curriculum_generator,
    curriculum_generator_agent
)
from .plan_validator.agent import (
    create_plan_validator,
    plan_validator_agent
)

__all__ = [
    'create_curriculum_generator',
    'curriculum_generator_agent',
    'create_plan_validator',
    'plan_validator_agent',
]

