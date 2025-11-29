"""
Curriculum Optimizer - LoopAgent

Iteratively refines curriculum plans until valid.
Runs generate → validate loop up to max_iterations times.
"""

from google.adk.agents import LoopAgent
from .curriculum_generator.agent import create_curriculum_generator
from .plan_validator.agent import create_plan_validator


def create_curriculum_optimizer() -> LoopAgent:
    """
    Factory function to create the Curriculum Optimizer loop agent.
    
    This agent:
    1. Generates a curriculum plan
    2. Validates the plan
    3. If invalid, loops back to regenerate (up to 3 times)
    4. Exits when plan is valid or max iterations reached
    
    Loop Flow:
    1. CurriculumGenerator → curriculum_draft
    2. PlanValidator → validation_result
       - If valid: calls exit_loop
       - If invalid: loop continues
    
    Returns:
        LoopAgent configured for curriculum optimization
    """
    return LoopAgent(
        name="curriculum_optimizer",
        description="Iteratively generates and validates curriculum plans until optimal",
        max_iterations=3,
        sub_agents=[
            create_curriculum_generator(),
            create_plan_validator()
        ]
    )


# Create singleton instance
curriculum_optimizer_agent = create_curriculum_optimizer()

