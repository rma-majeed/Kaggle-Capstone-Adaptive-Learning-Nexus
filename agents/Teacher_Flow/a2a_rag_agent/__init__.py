"""
A2A RAG Agent Package

CrewAI-based Textbook RAG Agent that communicates via A2A protocol.
This agent searches PDF textbooks to find educational content for teachers.
"""

from .agent import TextbookRagAgent

__all__ = ["TextbookRagAgent"]

