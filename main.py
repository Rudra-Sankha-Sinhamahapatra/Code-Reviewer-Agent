from langgraph.graph import StateGraph, END
from typing import List
import os
from dotenv import load_dotenv
from utils import ReviewBot, DEFAULT_EXCLUDED, get_github_repo, get_repository_files
from nodes import (
    analyze_code_changes,
    detect_code_patterns,
    check_security_issues,
    generate_review_feedback
)
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

load_dotenv()
console = Console()

def create_review_graph():
    """Creates the LangGraph workflow for code review"""
    graph = StateGraph(ReviewBot)

    # Nodes for each review stage
    graph.add_node("analyze_changes", analyze_code_changes)
    graph.add_node("detect_patterns", detect_code_patterns)
    graph.add_node("security_check", check_security_issues)
    graph.add_node("generate_feedback", generate_review_feedback)

    # Flow
    graph.set_entry_point("analyze_changes")
    graph.add_edge("analyze_changes","detect_patterns")
    graph.add_edge("detect_patterns", "security_check")
    graph.add_edge("security_check","generate_feedback")
    graph.add_edge("generate_feedback", END)

    return graph.compile()

def run_code_review(code_changes: List[dict]) -> dict:
    """Runs the complete code review workflow"""
    graph = create_review_graph()
    
    initial_state = {
        "code_changes": code_changes,
        "review_comments": [],
        "summary": "",
        "severity_level": "low",
        "suggestions": [],
        "patterns": [],
        "excluded_patterns": DEFAULT_EXCLUDED
    }
    
    result = graph.invoke(initial_state)
    return result


def run_github_review(repo_name: str, branch: str = "main") -> dict:
    """Runs code review on a GitHub repository"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment")
    
    console.print(f"[bold cyan]Connecting to GitHub repository: {repo_name}[/bold cyan]")
    
    try:
        # Get repository
        repo = get_github_repo(repo_name, token)
        console.print(f"[green]✓ Connected to {repo.full_name}[/green]")
        
        # Get all files
        console.print(f"[bold cyan]Fetching files from branch: {branch}[/bold cyan]")
        files = get_repository_files(repo, ref=branch)
        console.print(f"[green]✓ Found {len(files)} files[/green]")
        
        # Convert to our format
        code_changes = []
        for file in files:
            if file["content"] and file["path"].endswith(('.py', '.js', '.java', '.cpp', '.c', '.h')):
                code_changes.append({
                    "file_path": file["path"],
                    "line_number": 1,
                    "old_code": "",
                    "new_code": file["content"],
                    "change_type": "addition"
                })
        
        console.print(f"[green]✓ Analyzing {len(code_changes)} code files[/green]")
        
        return run_code_review(code_changes)
        
    except Exception as e:
        console.print(f"[red]Error accessing GitHub: {e}[/red]")
        return None



def interactive_mode():
    """Interactive mode for testing the code reviewer"""
    console.print("\n" + "="*80)
    console.print("[bold blue]AI Code Reviewer[/bold blue]")
    console.print("="*80)

    while True:
        console.print("\n[bold cyan]Choose an option:[/bold cyan]")
        console.print("1. Review a GitHub repository")
        console.print("2. Review sample code")
        console.print("3. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])
        
        if choice == "1":
            repo_name = Prompt.ask("Enter repository name (e.g., username/repo-name)")
            branch = Prompt.ask("Enter branch name", default="main")
            
            console.print(f"\n[bold yellow]Starting review of {repo_name}...[/bold yellow]")
            result = run_github_review(repo_name, branch)
            
            if result:
                display_results(result)
            else:
                console.print("[red]Review failed. Check your token and repository name.[/red]")

        elif choice == "2":
            # Sample code review (existing functionality)
            sample_changes = [
                {
                    "file_path": "example.py",
                    "line_number": 15,
                    "old_code": "def process_data(data):",
                    "new_code": "def process_data(data, config=None):",
                    "change_type": "modification"
                },
                {
                    "file_path": "example.py",
                    "line_number": 21,
                    "old_code": "",
                    "new_code": "def get_user_data(user_id):\n    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n    return execute_query(query)",
                    "change_type": "addition"
                },
                {
                    "file_path": "example.py",
                    "line_number": 26,
                    "old_code": "",
                    "new_code": "def load_config_file(filename):\n    file = open(filename, 'r')\n    config = json.load(file)\n    return config",
                    "change_type": "addition"
                },
                {
                    "file_path": "example.py",
                    "line_number": 70,
                    "old_code": "",
                    "new_code": "API_KEY = \"sk-1234567890abcdef\"\nDATABASE_PASSWORD = \"admin123\"",
                    "change_type": "addition"
                },
                {
                    "file_path": "example.py",
                    "line_number": 110,
                    "old_code": "",
                    "new_code": "def divide_numbers(a, b):\n    return a / b  # What if b is 0?",
                    "change_type": "addition"
                }
            ]
            
            console.print("\n[bold yellow]Running sample code review...[/bold yellow]")
            result = run_code_review(sample_changes)
            display_results(result)
            
        elif choice == "3":
            console.print("\n[bold green]Goodbye![/bold green]")
            break

def display_results(result):
    """Display review results"""
    console.print("\n" + "="*80)
    console.print("[bold green]REVIEW COMPLETE[/bold green]")
    console.print("="*80)
    
    console.print(Panel(
        result.get('summary', 'No summary generated'),
        title="[bold]Code Review Results[/bold]",
        border_style="green"
    ))
    
    if result.get('review_comments'):
        console.print("\n[bold]Detailed Comments:[/bold]")
        for comment in result['review_comments']:
            severity_color = {
                'low': 'green',
                'medium': 'yellow', 
                'high': 'red',
                'critical': 'red'
            }.get(comment['severity'], 'white')
            
            console.print(f"[{severity_color}]{comment['file_path']}:{comment['line_number']}[/{severity_color}] - {comment['comment']}")

if __name__ == "__main__":
    interactive_mode()