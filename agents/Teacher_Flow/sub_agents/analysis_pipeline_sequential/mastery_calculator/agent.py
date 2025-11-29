"""
Mastery Calculator Sub-Agent

Calculates and updates student mastery levels using MCP server.
Part of the AnalysisPipeline SequentialAgent.

This agent demonstrates MCP integration for the Kaggle requirement.
It connects to the mastery_mcp_server to calculate mastery using EMA formula.
"""

from google.adk.agents import LlmAgent
# Note: MCP tools will be connected at runtime via McpToolset
# For now, we create the agent without tools - tools will be added when running


def create_mastery_calculator() -> LlmAgent:
    """
    Factory function to create the Mastery Calculator agent.
    
    This agent:
    1. Receives analysis patterns from PatternAnalyzer
    2. Calculates updated mastery levels using MCP tools
    3. Saves mastery data for future use
    
    Note: MCP tools (calculate_mastery, get_mastery, etc.) will be
    connected at runtime using McpToolset.
    
    Returns:
        LlmAgent configured for mastery calculation
    """
    return LlmAgent(
        name="mastery_calculator",
        model="gemini-2.0-flash",
        description="Calculates and updates student mastery levels using MCP server",
        instruction="""
You are the Mastery Calculator. Your job is to calculate and update mastery levels.

## Your Task
Based on the pattern analysis, calculate updated mastery levels for the student.

## MCP Tools Available (connected at runtime)

### calculate_mastery
Updates mastery using Exponential Moving Average:
- new_mastery = (old_mastery * 0.8) + (new_score * 0.2)
- Args: student_id, topic, new_score

### get_mastery
Gets current mastery for a student-topic pair:
- Args: student_id, topic

### get_all_mastery
Gets all mastery levels for a student:
- Args: student_id

### bulk_update_mastery
Updates multiple mastery scores at once:
- Args: list of {student_id, topic, score}

## Calculation Process

1. **Get Current Mastery**:
   - Use get_all_mastery to see current levels
   - Note which topics have no history

2. **Calculate Updates**:
   - For each topic with new scores, use calculate_mastery
   - The tool applies the EMA formula automatically

3. **Report Results**:
   - Show before/after mastery levels
   - Highlight significant changes

## Output Format
```
MASTERY CALCULATION
===================
Student: [student_id]

Updated Mastery Levels:
| Topic       | Previous | New    | Change |
|-------------|----------|--------|--------|
| Fractions   | 0.65     | 0.72   | +0.07  |
| Decimals    | 0.42     | 0.48   | +0.06  |

Average Mastery: X.XX → X.XX
Improvement: +/-X.XX

Next Steps:
- Focus on: [weakest topic]
- Maintain: [strongest topic]
```

## Important
- Always use the MCP tools to calculate - don't compute manually
- Report both previous and new mastery levels
- Highlight improvement or decline
        """,
        tools=[],  # MCP tools connected at runtime via McpToolset
        output_key="mastery_levels"
    )


# Create singleton instance
mastery_calculator_agent = create_mastery_calculator()


# Factory function that includes MCP tools (for runtime use)
async def create_mastery_calculator_with_mcp():
    """
    Creates MasteryCalculator agent with MCP tools connected.
    
    This async function connects to the MCP server and returns
    an agent with the mastery calculation tools available.
    
    Usage:
        agent = await create_mastery_calculator_with_mcp()
    """
    from google.adk.tools import McpToolset
    from mcp import StdioConnectionParams
    from pathlib import Path
    
    # Path to MCP server
    mcp_server_path = Path(__file__).parent.parent.parent.parent / "tools" / "mastery_mcp_server.py"
    
    # Create MCP toolset
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            command="python",
            args=[str(mcp_server_path)]
        )
    )
    
    # Get tools from MCP server
    tools = await toolset.get_tools()
    
    # Create agent with MCP tools
    return LlmAgent(
        name="mastery_calculator",
        model="gemini-2.0-flash",
        description="Calculates and updates student mastery levels using MCP server",
        instruction="""
You are the Mastery Calculator. Your job is to calculate and update mastery levels.

## MCP Tools Available
- calculate_mastery(student_id, topic, new_score) - Update mastery with EMA
- get_mastery(student_id, topic) - Get current mastery
- get_all_mastery(student_id) - Get all mastery levels
- bulk_update_mastery(updates) - Batch update

## Your Task
1. Get current mastery levels using get_all_mastery
2. For new scores, use calculate_mastery to update
3. Report the changes in mastery levels

## Output
Show before/after mastery with changes, and recommend focus areas.
        """,
        tools=tools,
        output_key="mastery_levels"
    ), toolset  # Return both agent and toolset (for cleanup)

