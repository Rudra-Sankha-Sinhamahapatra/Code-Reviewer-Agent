
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console
from utils import ReviewBot, CodeChange, ReviewComment

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

IMPORTANT: You must respond with ONLY valid JSON in the exact format below. Do not include any text before or after the JSON.

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
}}"""

    try:
        response = llm.invoke(prompt).content
        
        # Debug:  the raw response to see what we're getting
        console.print(f"[dim]Raw AI response length: {len(response)} characters[/dim]")
        
       
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        
        if json_start != -1 and json_end != -1:
            json_str = response[json_start:json_end]
            console.print(f"[dim]Extracted JSON preview: {json_str[:100].replace('[', '\\[').replace(']', '\\]')}...[/dim]")
            
            try:
                analysis = json.loads(json_str)
            except json.JSONDecodeError as json_error:
                console.print(f"[yellow]JSON parsing failed, trying to clean response...[/yellow]")
               
                cleaned_json = json_str.replace("'", '"').replace('\n', ' ').strip()
                
                # If still fails, try extracting just the comments manually
                try:
                    analysis = json.loads(cleaned_json)
                except json.JSONDecodeError:
                    console.print(f"[red]Failed to parse JSON. Creating manual analysis...[/red]")

                    analysis = {
                        "comments": [],
                        "overall_assessment": "Analysis completed but JSON parsing failed. Code appears to have issues that need manual review."
                    }

            comments = []
            for comment_data in analysis.get("comments", []):
                try:
                    comment = ReviewComment(
                        file_path=comment_data.get("file_path", "unknown"),
                        line_number=comment_data.get("line_number", 1),
                        comment=comment_data.get("comment", "No comment provided"),
                        severity=comment_data.get("severity", "medium"),
                        category=comment_data.get("category", "general")
                    )
                    comments.append(comment)
                except Exception as comment_error:
                    console.print(f"[yellow]Skipping malformed comment: {comment_error}[/yellow]")

            state["review_comments"] = comments
            state["summary"] = analysis.get("overall_assessment", "Analysis completed")

            console.print(f"[green]Analysis complete! Found {len(comments)} issues[/green]")
        else:
            console.print(f"[yellow]No JSON found in response. Raw response: {response[:200]}...[/yellow]")
            state["summary"] = "Analysis completed but no structured results were returned."

    except Exception as e:
        console.print(f"[red]Error in analysis: {e}[/red]")
        console.print(f"[dim]Full error details: {str(e)}[/dim]")
        #  a default state even if everything fails
        state["review_comments"] = []
        state["summary"] = f"Analysis failed due to error: {str(e)}"
    
    return state

def detect_code_patterns(state: ReviewBot) -> ReviewBot:
    """Detects anti-patterns and common issues across multiple languages"""
    console.print("[bold cyan]Detecting code patterns...[/bold cyan]")
    
    if not state.get("code_changes"):
        console.print("[yellow]No code changes to analyze for patterns[/yellow]")
        return state
    
    #  patterns that work across languages
    ANTI_PATTERNS = {
        "debug_statements": ["print(", "console.log(", "console.error(", "println!", "fmt.print", "cout <<"],
        "todo_comments": ["todo", "fixme", "hack", "xxx", "note:", "bug:"],
        "large_files": 100,  # lines threshold
        "long_lines": 120,   # character threshold
        "magic_numbers": ["= 42", "= 100", "= 1000", "* 24", "* 60", "* 365"]
    }
    
    GOOD_PATTERNS = {
        "tests": ["test_", "it(", "describe(", "should", "expect(", "_test."],
        "error_handling": ["try", "catch", "except", "Result<", "Option<", "?."],
        "documentation": ["/**", "///", '"""', "# ", "//"],
        "type_safety": [": string", ": number", ": bool", "String", "Option", "Result"]
    }
    
    patterns_found = []
    anti_patterns = []
    
    for change in state["code_changes"]:
        code = change.get("new_code", "")
        code_lower = code.lower()
        file_path = change.get("file_path", "")
        lines = code.split('\n')
        
        # Check anti-patterns
        for pattern_type, keywords in ANTI_PATTERNS.items():
            if pattern_type == "large_files":
                if len([l for l in lines if l.strip()]) > keywords:
                    anti_patterns.append(f"Large file ({len(lines)} lines) in {file_path}")
            elif pattern_type == "long_lines":
                long_lines = [i for i, line in enumerate(lines, 1) if len(line) > keywords]
                if long_lines:
                    anti_patterns.append(f"Long lines detected in {file_path} (lines: {long_lines[:3]})")
            else:
                found_keywords = [kw for kw in keywords if kw in code_lower]
                if found_keywords:
                    anti_patterns.append(f"{pattern_type.replace('_', ' ').title()} in {file_path}: {found_keywords[:2]}")
        
        # Check good patterns
        for pattern_type, keywords in GOOD_PATTERNS.items():
            found_keywords = [kw for kw in keywords if kw in code_lower]
            if found_keywords:
                patterns_found.append(f"{pattern_type.replace('_', ' ').title()} in {file_path}")
    
   
    state["patterns"] = patterns_found
    existing_comments = state.get("review_comments", [])
    
    # anti-patterns as comments
    for anti_pattern in anti_patterns:
        existing_comments.append(ReviewComment(
            file_path="pattern_analysis",
            line_number=1,
            comment=anti_pattern,
            severity="low",
            category="code_smell"
        ))
    
    state["review_comments"] = existing_comments
    console.print(f"[green]Pattern detection complete! Found {len(patterns_found)} good patterns and {len(anti_patterns)} anti-patterns[/green]")
    
    return state

def check_security_issues(state: ReviewBot) -> ReviewBot:
    """Checks for security vulnerabilities"""
    console.print("[bold cyan]Checking security...[/bold cyan]")
    
    if not state.get("code_changes"):
        console.print("[yellow]No code changes to check for security issues[/yellow]")
        return state
    
    security_issues = []
    existing_comments = state.get("review_comments", [])
    
    for change in state["code_changes"]:
        code = change.get("new_code", "")
        file_path = change.get("file_path", "")
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower().strip()
            
            # Check for hardcoded secrets
            if any(secret in line_lower for secret in ['password', 'api_key', 'secret', 'token']):
                if '=' in line and any(quote in line for quote in ['"', "'"]):
                    security_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "issue": "Potential hardcoded secret detected",
                        "severity": "high"
                    })
            
            # Check for SQL injection patterns
            if 'select * from' in line_lower or 'insert into' in line_lower:
                if 'format(' in line_lower or '{' in line:
                    security_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "issue": "Potential SQL injection vulnerability",
                        "severity": "critical"
                    })
            
            # Check for unsafe file operations
            if 'open(' in line_lower and 'w' in line:
                if '/tmp/' in line_lower or '../' in line_lower:
                    security_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "issue": "Unsafe file path detected",
                        "severity": "medium"
                    })
            
     
            if any(func in line_lower for func in ['eval(', 'exec(', 'compile(']):
                security_issues.append({
                    "file": file_path,
                    "line": line_num,
                    "issue": "Unsafe code execution function detected",
                    "severity": "high"
                })
    

    for issue in security_issues:
        security_comment = ReviewComment(
            file_path=issue["file"],
            line_number=issue["line"],
            comment=f"SECURITY: {issue['issue']}",
            severity=issue["severity"],
            category="security"
        )
        existing_comments.append(security_comment)
    
    state["review_comments"] = existing_comments
    
    console.print(f"[green]Security check complete! Found {len(security_issues)} potential security issues[/green]")
    
    return state


def generate_review_feedback(state: ReviewBot) -> ReviewBot:
    """Generates final review feedback"""
    console.print("[bold cyan]Generating feedback...[/bold cyan]")
    
    comments = state.get("review_comments", [])
    patterns = state.get("patterns", [])

    if not comments:
        state["summary"] = "✅ Code review complete: No significant issues found!"
        state["suggestions"] = [
            "Code appears to follow good practices",
            "Consider adding more documentation if needed",
            "Keep up the good work!"
        ]
        return state
    
    if not state.get("review_comments"):
        state["summary"] = "No issues found in the code changes."
        return state
    
    critical = [c for c in comments if c["severity"] == "critical"]
    high = [c for c in comments if c["severity"] == "high"]
    medium = [c for c in comments if c["severity"] == "medium"]
    low = [c for c in comments if c["severity"] == "low"]
    
    security_issues = [c for c in comments if c["category"] == "security"]
    best_practice_issues = [c for c in comments if c["category"] == "best_practice"]
    code_smell_issues = [c for c in comments if c["category"] == "code_smell"]

    suggestions = []
    if critical or high:
        suggestions.append("🔴 URGENT: Address critical and high-severity issues immediately")
    if security_issues:
        suggestions.append("🔒 SECURITY: Review and fix all security vulnerabilities")
    if medium:
        suggestions.append("🟡 Address medium-priority issues before next release")
    if best_practice_issues:
        suggestions.append("📚 Consider improving code following best practices")

    summary = f"""📊 Code Review Summary:

🔍 ANALYSIS RESULTS:
• Total Issues: {len(comments)}
• Critical: {len(critical)} | High: {len(high)} | Medium: {len(medium)} | Low: {len(low)}

📂 BY CATEGORY:
• Security Issues: {len(security_issues)}
• Best Practice Issues: {len(best_practice_issues)}
• Code Smells: {len(code_smell_issues)}
• Other Issues: {len(comments) - len(security_issues) - len(best_practice_issues) - len(code_smell_issues)}

🎯 GOOD PATTERNS FOUND: {len(patterns)}

🚨 TOP PRIORITY ISSUES:"""
    
 
    priority_issues = sorted(comments, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x["severity"], 0), reverse=True)
    
    for i, issue in enumerate(priority_issues[:5], 1):
        severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(issue["severity"], "⚪")
        summary += f"\n{i}. {severity_emoji} {issue['file_path']}:{issue['line_number']} - {issue['comment'][:100]}{'...' if len(issue['comment']) > 100 else ''}"
    
    state["summary"] = summary
    state["suggestions"] = suggestions
    
    console.print(f"[green]Feedback generation complete! Generated {len(suggestions)} actionable suggestions[/green]")
    
    return state