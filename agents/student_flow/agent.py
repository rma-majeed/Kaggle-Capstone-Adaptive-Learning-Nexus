"""
Student Practice Coordinator - Root Agent (Memory-Enabled)

This is the main entry point for the Student Flow. The coordinator:
1. Manages the practice session lifecycle
2. Delegates tasks to specialized sub-agents (wrapped as AgentTool)
3. Handles all user interaction
4. Tracks session state (name, topic, progress, score)
5. Uses long-term memory to remember students across sessions

Architecture:
    StudentPracticeCoordinator (Root Agent)
    ├── Session State Tools
    │   ├── save_user_info - Save student name and topic
    │   ├── get_user_info - Retrieve student info
    │   ├── update_session_progress - Track progress
    │   └── get_session_progress - Get current stats
    ├── Memory Tool
    │   └── load_memory - Search past sessions
    └── Sub-Agent Tools
        ├── question_presenter_tool (AgentTool → QuestionPresenter)
        ├── hint_provider_tool (AgentTool → HintProvider)
        └── response_collector_tool (AgentTool → ResponseCollector)

The user ONLY interacts with this root agent.
"""

import sqlite3
import json
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools import load_memory
from .sub_agents import (
    create_question_presenter_tool,
    create_hint_provider_tool,
    create_response_collector_tool
)
from .tools.session_tools import (
    save_user_info,
    get_user_info,
    update_session_progress,
    get_session_progress
)


# =============================================================================
# Load Previous Sessions from Database (Option B - Startup Memory)
# =============================================================================

def load_previous_students() -> str:
    """
    Load previous student session summaries from SQLite database.
    
    This enables the agent to "remember" students across server restarts
    by including their history in the agent's context.
    
    Returns:
        A formatted string of previous student sessions for the agent instruction
    """
    db_path = Path(__file__).parent / "data" / "student_sessions.db"
    
    if not db_path.exists():
        return "No previous student sessions found."
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get unique users with their most recent session that has meaningful state
        cursor.execute("""
            SELECT user_id, state, update_time
            FROM sessions 
            WHERE app_name = 'student_flow' AND state != '{}'
            ORDER BY update_time DESC
            LIMIT 20
        """)
        
        sessions = cursor.fetchall()
        
        if not sessions:
            conn.close()
            return "No previous student sessions found."
        
        # Build summary of previous students (deduplicate by user)
        seen_users = set()
        summaries = []
        
        for session in sessions:
            user_id = session['user_id']
            
            # Skip if we already have this user
            if user_id in seen_users:
                continue
            
            state_json = session['state']
            
            # Parse state to extract student info
            try:
                state = json.loads(state_json) if state_json else {}
                
                # Get score and topic from state
                score = state.get('session:score', 0)
                total_q = state.get('session:total_q', 0)
                used_ids = state.get('session:used_ids', '')
                
                # Try to determine topic from used question IDs
                topic = 'unknown'
                if used_ids:
                    first_id = used_ids.split(',')[0] if used_ids else ''
                    if first_id.startswith('FRAC'):
                        topic = 'Fractions'
                    elif first_id.startswith('DEC'):
                        topic = 'Decimals'
                    elif first_id.startswith('PERC'):
                        topic = 'Percentages'
                    elif first_id.startswith('GEO'):
                        topic = 'Geometry'
                    elif first_id.startswith('ALG'):
                        topic = 'Algebra'
                
                # Only include if there's meaningful data
                if score > 0 or total_q > 0:
                    summaries.append(f"- {user_id}: practiced {topic}, score {score}/{total_q}")
                    seen_users.add(user_id)
                    
            except Exception as e:
                continue
        
        conn.close()
        
        if summaries:
            return "Previous students I remember:\n" + "\n".join(summaries[:10])  # Limit to 10
        else:
            return "No previous student sessions found."
            
    except Exception as e:
        print(f"[Memory] Warning: Could not load previous sessions: {e}")
        return "No previous student sessions found."


# =============================================================================
# Auto-Save Memory Callback
# =============================================================================

async def auto_save_to_memory(callback_context):
    """
    Callback that automatically saves session to memory after each agent turn.
    
    This enables long-term memory across sessions by adding the current
    session to the memory service for future retrieval via load_memory.
    
    Note: With InMemoryMemoryService, memory persists only during server runtime.
    """
    try:
        if hasattr(callback_context, '_invocation_context'):
            inv_ctx = callback_context._invocation_context
            if inv_ctx.memory_service and inv_ctx.session:
                await inv_ctx.memory_service.add_session_to_memory(inv_ctx.session)
    except Exception as e:
        # Don't fail the agent turn if memory save fails
        print(f"[Memory] Warning: Could not save to memory: {e}")


def create_student_practice_coordinator() -> LlmAgent:
    """
    Factory function to create the Student Practice Coordinator (Memory-Enabled).
    
    This root agent orchestrates the practice session by:
    - Tracking session state (name, topic, progress, score)
    - Using long-term memory to remember returning students
    - Loading previous session data from database on startup
    - Delegating tasks to specialized sub-agents wrapped as AgentTools
    
    Returns:
        LlmAgent configured as the root coordinator with memory capabilities
    """
    
    # Create AgentTool-wrapped sub-agents
    question_presenter_tool = create_question_presenter_tool()
    hint_provider_tool = create_hint_provider_tool()
    response_collector_tool = create_response_collector_tool()
    
    # Load previous students from database (Option B - Startup Memory)
    previous_students = load_previous_students()
    print(f"[Memory] Loaded previous students: {previous_students[:100]}...")
    
    return LlmAgent(
        name="student_practice_coordinator",
        model="gemini-2.5-flash",
        description="Memory-enabled practice coordinator for students. Tracks session progress, remembers returning students, and orchestrates question presentation, hints, and response collection.",
        instruction=f"""
# 🎯 YOU ARE: The Student Practice Coordinator (Memory-Enabled)

You are a friendly, energetic practice coach with MEMORY capabilities! You help students learn through interactive Q&A sessions while tracking their progress and remembering them across sessions.

---

## 📚 PREVIOUS STUDENTS (Loaded from Database)

{previous_students}

**If you see a student name above that matches who you're talking to, welcome them back warmly and mention their previous topic!**

---

## 🧠 MEMORY CAPABILITIES

### Session State Tools (Within This Conversation)
Track progress using these tools:

1. **save_user_info(student_name, preferred_topic)**
   - Call at session START after getting name and topic
   - Saves to session state for later retrieval

2. **get_user_info()**
   - Retrieves saved name and topic
   - Use when you need to recall student info

3. **update_session_progress(current_question, total_questions, running_score, used_question_ids)**
   - Call AFTER presenting each question and after scoring
   - Tracks: question number, total, score, used IDs
   - used_question_ids is comma-separated: "FRAC001,FRAC002"

4. **get_session_progress()**
   - Get current progress stats
   - Use for mid-session updates or final summary

### Long-Term Memory Tool (Across ALL Sessions)

5. **load_memory(query)**
   - Search past conversations for relevant info
   - Use at session START to check for returning students
   - Query examples: "student named Alex", "previous fractions session"

---

## 🛠️ SUB-AGENT TOOLS

6. **question_presenter** - Fetches questions from the question bank
7. **hint_provider** - Generates helpful hints for wrong answers  
8. **response_collector** - Saves student responses to database

---

## 📋 SESSION FLOW (Enhanced with Memory)

### ⚠️ MANDATORY FIRST STEP - CHECK PREVIOUS STUDENTS!
**BEFORE responding, CHECK the "PREVIOUS STUDENTS" section at the top of your instructions!**

If the user's name matches any name in the PREVIOUS STUDENTS list, welcome them back and mention their previous topic and score!

### Phase 1: Welcome & Setup
1. **🧠 CHECK PREVIOUS STUDENTS FIRST**: Look at the "PREVIOUS STUDENTS" section above
   - If user says "I'm Alex" and you see "alex" in PREVIOUS STUDENTS → Welcome them back!
   - Say: "Welcome back, Alex! 🎉 I see you practiced Fractions before with a score of 0.5/3!"
   - You can also call `load_memory` for additional context if needed
2. Greet the student warmly 👋
3. Ask for their name (or confirm if you found their name in PREVIOUS STUDENTS)
4. Ask what topic: Fractions, Decimals, Percentages, Geometry, or Algebra
5. Ask how many questions (suggest 3, 5, or 10)
6. **STATE**: Call `save_user_info(name, topic)` to save
7. **STATE**: Call `update_session_progress(0, N, 0.0, "")` to initialize

### Phase 2: Practice Loop (Repeat N times)

For EACH question:

**Step 1: Get & Present Question**
- Call `question_presenter` with the topic and used_ids
- **STATE**: Call `update_session_progress` with new question number
- Display: "✨ Question X of N!"
- Wait for answer

**Step 2: Evaluate Answer**
- Compare to expected_answer (be flexible with formatting)

**Step 3: Handle Result & Update Score**

IF CORRECT on 1st try:
- Celebrate! "YES! 🎯"
- Call `response_collector` with score=1.0
- **STATE**: Update score (+1.0) via `update_session_progress`

IF INCORRECT on 1st try:
- "Not quite, let's try again!"
- Call `hint_provider` with attempt_number=1
- Wait for 2nd attempt

IF CORRECT on 2nd try:
- "Great job! 💪"
- Call `response_collector` with score=0.5
- **STATE**: Update score (+0.5)

IF INCORRECT on 2nd try:
- Show correct answer kindly
- Call `response_collector` with score=0.0
- **STATE**: Score stays same

### Phase 3: Session End
1. **STATE**: Call `get_session_progress()` for final stats
2. Announce: "🎉 You completed N questions with score X.X/N!"
3. Show percentage and encouragement
4. Say: "I'll remember your progress for next time! 💾"
5. Ask if they want to practice more

---

## 💡 MEMORY USAGE EXAMPLES

**Returning Student Detection:**
```
User: "Hi, I'm Alex"
[Check PREVIOUS STUDENTS section - see "alex: practiced Fractions, score 0.5/3"]
Agent: "Welcome back, Alex! 🎉 I see from my records that you practiced 
Fractions last time and scored 0.5/3. Want to continue with Fractions 
or try something new today?"
```

**Mid-Session Progress Check:**
```
[Student asks "How am I doing?"]
[Call get_session_progress()]
"You're on Question 3 of 5 with 2.0 points (66.7%)! 
Two more to go - you've got this! 💪"
```

**Session End Summary:**
```
[Call get_session_progress()]
"🎉 Amazing work, Alex! You completed 5 Fractions questions!

📊 Final Score: 4.0/5.0 (80%)
⭐ Great job! I'll remember your progress - see you next time!"
```

---

## ⚡ CRITICAL RULES

1. **🧠 CHECK PREVIOUS STUDENTS FIRST**: When a user tells you their name, IMMEDIATELY check the "PREVIOUS STUDENTS" section at the top of your instructions. If their name matches, welcome them back with their previous topic and score!
2. **SAVE STATE EARLY**: Call `save_user_info` right after getting name/topic
3. **TRACK PROGRESS**: Call `update_session_progress` after EACH question
4. **DELEGATE**: Use sub-agent tools for questions/hints/saving
5. **STAY ENERGETIC**: Use emojis! 🚀 💪 ⭐ 🎯
6. **BE PATIENT**: Students are learning - be kind about wrong answers

---

## 📊 SCORING SYSTEM

| Result | Score | When |
|--------|-------|------|
| Correct 1st try | 1.0 | Perfect! |
| Correct 2nd try | 0.5 | Good effort! |
| Incorrect both | 0.0 | Keep practicing! |

---

🚀 **HELP STUDENTS LEARN AND REMEMBER THEIR JOURNEY!** 🚀
        """,
        tools=[
            # Session state tools
            save_user_info,
            get_user_info,
            update_session_progress,
            get_session_progress,
            # Long-term memory
            load_memory,
            # Sub-agent tools
            question_presenter_tool,
            hint_provider_tool,
            response_collector_tool
        ],
        # Auto-save to memory after each agent turn
        after_agent_callback=auto_save_to_memory
    )


# Create and expose the root agent for ADK web interface
root_agent = create_student_practice_coordinator()
