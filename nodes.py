from typing import List
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console
from rich.panel import Panel
from utils import ReviewBot, CodeChange, ReviewComment

# Load environment variables
load_dotenv()

console = Console()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_output_tokens=4000
)

def analyze_code_changes(state: ReviewBot) -> ReviewBot:
    """Analyzes code changes for style, complexity, and documentation issues"""
    console.print("[bold cyan]Analyzing code changes...[/bold cyan]")

    if not state.get("code_changes"):
        console.print("[yellow]No code changes to analyze[/yellow]")
        return state


    changes_text = ""
    for change in state["code_changes"]:
        changes_text += f"\nFile: {change['file_path']}:{change['line_number']}\n"
        changes_text += f"Type: {change['change_type']}\n"
        changes_text += f"Old: {change['old_code']}\n"
        changes_text += f"New: {change['new_code']}\n"
        changes_text += "-" * 50 + "\n"

    prompt = f"""Analyze these code changes as an expert code reviewer.

CODE CHANGES:
{changes_text}

REVIEW INSTRUCTIONS:
1. Code Quality:
   - Check for clean code principles
   - Identify complexity issues
   - Assess naming conventions
   - Evaluate code organization

2. Best Practices:
   - Verify error handling
   - Check resource management
   - Review API design
   - Assess testability

Provide specific, actionable feedback in JSON format:
{{
    "comments": [
        {{
            "file_path": "file.py",
            "line_number": 10,
            "comment": "Consider extracting this logic into a separate function",
            "severity": "medium",
            "category": "best_practice"
        }}
    ],
    "overall_assessment": "Overall good changes with room for improvement",
    "priority_issues": ["List of high-priority issues"]
}}

RESPONSE (JSON only):"""

    try:
        response = llm.invoke(prompt).content

        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start != -1 and json_end != -1:
            analysis = json.loads(response[json_start:json_end])

            comments = []
            for comment_data in analysis.get("comments", []):
                comment = ReviewComment(
                    file_path=comment_data["file_path"],
                    line_number=comment_data["line_number"],
                    comment=comment_data["comment"],
                    severity=comment_data["severity"],
                    category=comment_data["category"]
                )
                comments.append(comment)

            state["review_comments"] = comments
            state["summary"] = analysis.get("overall_assessment", "")

            console.print(f"[green]Analysis complete! Found {len(comments)} issues[/green]")

    except Exception as e:
        console.print(f"[red]Error in analysis: {e}[/red]")
    
    return state

def detect_code_patterns(state: ReviewBot) -> ReviewBot:
    """Detects anti-patterns and common issues"""
    console.print("[bold cyan]Detecting code patterns...[/bold cyan]")
    
    # Implementation for pattern detection
    # This would look for common anti-patterns, code smells, etc.
    
    return state

def check_security_issues(state: ReviewBot) -> ReviewBot:
    """Checks for security vulnerabilities"""
    console.print("[bold cyan]Checking security...[/bold cyan]")
    
    # Implementation for security checks
    # This would look for common security issues
    
    return state


def generate_review_feedback(state: ReviewBot) -> ReviewBot:
    """Generates final review feedback"""
    console.print("[bold cyan]Generating feedback...[/bold cyan]")
    
    if not state.get("review_comments"):
        state["summary"] = "No issues found in the code changes."
        return state
    
    # Generate summary based on comments
    high_priority = [c for c in state["review_comments"] if c["severity"] in ["high", "critical"]]
    medium_priority = [c for c in state["review_comments"] if c["severity"] == "medium"]
    low_priority = [c for c in state["review_comments"] if c["severity"] == "low"]
    
    summary = f"""Code Review Summary:
    
Total Issues Found: {len(state["review_comments"])}
High Priority: {len(high_priority)}
Medium Priority: {len(medium_priority)}
Low Priority: {len(low_priority)}

Key Areas for Improvement:
"""

    
    for comment in state["review_comments"][:5]:  # Top 5 issues
        summary += f"\n• {comment['file_path']}:{comment['line_number']} - {comment['comment']}"
    
    state["summary"] = summary
    return state

    