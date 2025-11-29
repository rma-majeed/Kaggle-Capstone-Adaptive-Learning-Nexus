# Educational Personalized Learning Coach

**Framework**: Google ADK
**Date**: 2025-11-26
**Purpose**: Kaggle AI Agents Competition

## System Overview
A two-persona learning platform demonstrating advanced ADK agent orchestration:
- **Student Flow**: Interactive Q&A practice sessions with adaptive questioning
- **Teacher Flow**: Automated data analysis and curriculum optimization for each student.

## Folder Structure
```
agents/
├─ README.md
├─ __init__.py
│
├─ student_flow/
│  ├─ __init__.py
│  ├─ agent.py (StudentPracticeCoordinator - root)
│  │
│  └─ sub_agents/
│     ├─ __init__.py
│     ├─ question_presenter/
│     │  └─ agent.py
│     ├─ hint_provider/
│     │  └─ agent.py
│     └─ response_collector/
│        └─ agent.py
│
├─ teacher_flow/
│  ├─ __init__.py
│  ├─ agent.py (TeacherAnalysisCoordinator - root)
│  │
│  └─ sub_agents/
│     ├─ __init__.py
│     │
│     ├─ data_fetcher_parallel/
│     │  ├─ agent.py (ParallelAgent)
│     │  ├─ student_data_retriever/
│     │  │  └─ agent.py
│     │  ├─ question_data_retriever/
│     │  │  └─ agent.py
│     │  └─ historical_performance/
│     │     └─ agent.py
│     │
│     ├─ analysis_pipeline_sequential/
│     │  ├─ agent.py (SequentialAgent)
│     │  ├─ answer_scorer/
│     │  │  └─ agent.py
│     │  ├─ pattern_analyzer/
│     │  │  └─ agent.py
│     │  └─ mastery_calculator/
│     │     └─ agent.py
│     │
│     ├─ curriculum_optimizer_loop/
│     │  ├─ agent.py (LoopAgent)
│     │  ├─ curriculum_generator/
│     │  │  └─ agent.py
│     │  └─ plan_validator/
│     │     └─ agent.py
│     │
│     └─ report_generator_sequential/
│        ├─ agent.py (SequentialAgent)
│        ├─ summary_creator/
│        │  └─ agent.py
│        ├─ recommendation_engine/
│        │  └─ agent.py
│        └─ visualization_data/
│           └─ agent.py
```
