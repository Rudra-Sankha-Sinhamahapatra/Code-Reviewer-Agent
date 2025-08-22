
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console
from utils import ReviewBot, ReviewComment
import re

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
    for i, change in enumerate(state["code_changes"][:4]): #Limit is 4, only it will review first 4 files
        new_code = change['new_code']
        if len(new_code) > 800:
            new_code = new_code[:800] + "\n.. (truncated)"

        changes_text += f"\nFile {i+1}: {change['file_path']}\n"
        changes_text += f"Code:\n{new_code}\n"
        changes_text += "-" * 40 + "\n"

    prompt = f"""You are an expert code reviewer in the Industry who only returns JSON object

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
    "overall_assessment": "Overall good changes with room for improvement"
}}"""

    try:
        response = llm.invoke(prompt).content
        console.print(f"[dim]Raw AI response length: {len(response)} characters[/dim]")
        
        json_data = None

        # Strategy 1: Look for complete JSON object
        if response.startswith('{') and response.endswith('}'):
            try:
                json_data = json.loads(response)
            except:
                pass
        
         # Strategy 2: Find JSON between braces
        if not json_data:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                try:
                    json_data = json.loads(json_str)
                except:
                    # Strategy 3: Clean common issues
                    cleaned = json_str.replace("'", '"').replace('\n', ' ')
                    try:
                        json_data = json.loads(cleaned)
                    except:
                        pass
        
         # Strategy 4: Use regex to extract JSON-like content
        if not json_data:
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            for match in matches:
                try:
                    json_data = json.loads(match)
                    break
                except:
                    continue
        
         # If all fails, create a simple analysis
        if not json_data:
            console.print("[yellow]Could not parse JSON, creating manual analysis[/yellow]")
            json_data = {
                "comments": [
                    {
                        "file_path": "analysis",
                        "line_number": 1,
                        "comment": "AI returned unparseable response - manual review recommended",
                        "severity": "low",
                        "category": "general"
                    }
                ],
                "overall_assessment": "Analysis completed with parsing issues"
            }
        
        comments = []
        for comment_data in json_data.get("comments", []):
            try:
                comment = ReviewComment(
                    file_path=comment_data.get("file_path", "unknown"),
                    line_number=comment_data.get("line_number", 1),
                    comment=comment_data.get("comment", "No comment"),
                    severity=comment_data.get("severity", "medium"),
                    category=comment_data.get("category", "general")
                )
                comments.append(comment)
            except Exception as e:
                console.print(f"[dim]Skipping malformed comment: {e}[/dim]")

        state["review_comments"] = comments
        state["summary"] = json_data.get("overall_assessment", "Analysis completed")
        
        console.print(f"[green]Analysis complete! Found {len(comments)} issues[/green]")

    except Exception as e:
        console.print(f"[red]Analysis error: {e}[/red]")
        state["review_comments"] = []
        state["summary"] = "Analysis failed due to technical issues"
    
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
            
            #Skip empty lines or comments
            if not line_lower or line_lower.startswith('#') or line_lower.startswith('//'):
                continue
            
            secret_indicators = ['password', 'api_key', 'secret_key', 'token', 'apikey']
            # Check for hardcoded secrets
            if any(secret in line_lower for secret in secret_indicators):
                if '=' in line and any(quote in line for quote in ['"', "'"]):
                    value_part = line.split('=',1)[1].strip()

                    if not any(skip in value_part.lower() for skip in ['getenv', 'env.', 'process.env', 'config.', '${', 'none', 'null', '""', "''"]):
                      security_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "issue": "Potential hardcoded secret detected",
                        "severity": "high"
                    })
            
            # Check for SQL injection patterns
            sql_keywords = ['select ', 'insert ', 'update ', 'delete ', 'drop ', 'create ']
            if any(sql in line_lower for sql in sql_keywords):
                # Only flag if there's string formatting or concatenation
                if any(pattern in line for pattern in ['f"', "f'", '.format(', '%s', '%d', '+ ', '+=']):
                    # Skip if using parameterized queries
                    if not any(safe in line_lower for safe in ['execute(', 'prepare(', '?', ':param']):
                        security_issues.append({
                            "file": file_path,
                            "line": line_num,
                            "issue": "Potential SQL injection - use parameterized queries",
                            "severity": "critical"
                        })
            
            # Check for unsafe file operations
            unsafe_functions = ['eval(', 'exec(', 'compile(']
            if any(func in line_lower for func in unsafe_functions):
                # Skip if it's in comments or strings
                if not any(marker in line for marker in ['#', '//', '"""', "'''"]):
                    security_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "issue": f"Unsafe code execution function detected: {line.strip()[:50]}...",
                        "severity": "high"
                    })
            
            # File path traversal detection
            if any(pattern in line_lower for pattern in ['../', '../', '..\\', 'traversal']):
                if 'open(' in line_lower or 'file(' in line_lower:
                    security_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "issue": "Potential path traversal vulnerability",
                        "severity": "medium"
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