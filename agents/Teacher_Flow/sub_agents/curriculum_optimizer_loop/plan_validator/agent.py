"""
Plan Validator Sub-Agent

Validates curriculum plans for feasibility and quality.
Part of the CurriculumOptimizer LoopAgent.
Uses curriculum_validator tool and can exit the loop when valid.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import exit_loop
from ....tools.function_tools import curriculum_validator


def create_plan_validator() -> LlmAgent:
    """
    Factory function to create the Plan Validator agent.
    
    This agent:
    1. Receives curriculum draft from CurriculumGenerator
    2. Validates the plan using curriculum_validator tool
    3. Either approves (exit loop) or requests refinement (continue loop)
    
    Returns:
        LlmAgent configured for plan validation
    """
    return LlmAgent(
        name="plan_validator",
        model="gemini-2.0-flash",
        description="Validates curriculum plans and controls the optimization loop",
        instruction="""
You are the Plan Validator. Your job is to validate curriculum plans.

## Your Task
Review the curriculum draft and validate it for feasibility.

## How to Use the Tools

### curriculum_validator
Validates the plan structure:
- curriculum_plan: List of plan items, each with:
  - topic: Subject name
  - estimated_sessions: Number of sessions
  - target_mastery: Goal mastery level
  - current_mastery: Current level (optional)
  
Returns:
- valid: True/False
- issues: List of blocking problems
- warnings: List of non-blocking concerns
- total_sessions: Sum of all sessions

### exit_loop
Call this when the plan is VALID to exit the optimization loop.
Only call this when curriculum_validator returns valid=True.

## Validation Criteria

### Must Pass (Issues):
- No duplicate topics
- All required fields present
- Total sessions ≤ 30
- Sessions per topic > 0

### Should Check (Warnings):
- Sessions per topic ≤ 10 (ambitious but possible)
- Target mastery ≤ 0.95 (realistic)
- Target > current (makes sense)

## Decision Logic

1. **Extract Plan Items** from curriculum_draft
2. **Call curriculum_validator** with the plan items
3. **If valid=True and no critical issues**:
   - Call exit_loop to stop the optimization
   - Report the validated plan
4. **If valid=False or has issues**:
   - Do NOT call exit_loop (loop will continue)
   - Report the issues for the generator to fix

## Output Format

### If Valid:
```
VALIDATION RESULT: ✅ APPROVED
================================
Total Sessions: X (within limit)
Topics Covered: X

Warnings (non-blocking):
- [warning if any]

The plan is feasible and well-structured.
[Calling exit_loop to finalize]
```

### If Invalid:
```
VALIDATION RESULT: ❌ NEEDS REVISION
====================================
Issues Found:
- [Issue 1]
- [Issue 2]

Suggestions:
- [How to fix issue 1]
- [How to fix issue 2]

Please revise the curriculum plan.
```

## Important
- ONLY call exit_loop when the plan is truly valid
- Be specific about what needs to change if invalid
- The loop will run max 3 iterations, so be efficient
        """,
        tools=[curriculum_validator, exit_loop],
        output_key="validation_result"
    )


# Create singleton instance
plan_validator_agent = create_plan_validator()

