# example.py - Sample code with various issues for AI Code Review

import os
import json
import requests

# Bad practice: Global variable
data_cache = {}

def process_data(data, config=None):
    """Process data with optional configuration"""
    if config and config.get('validate'):
        validate_data(data)
    return data

# Security issue: Potential SQL injection
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # This is vulnerable to SQL injection
    return execute_query(query)

# Poor error handling
def load_config_file(filename):
    file = open(filename, 'r')
    config = json.load(file)
    return config

# Complex function that should be broken down
def process_user_request(request_data):
    # Validate input
    if not request_data:
        return None
    if 'user_id' not in request_data:
        return None
    if 'action' not in request_data:
        return None
    
    # Get user data
    user = get_user_data(request_data['user_id'])
    if not user:
        return None
    
    # Process action
    if request_data['action'] == 'update_profile':
        # Update profile logic
        profile_data = request_data.get('profile', {})
        user['name'] = profile_data.get('name', user['name'])
        user['email'] = profile_data.get('email', user['email'])
        user['phone'] = profile_data.get('phone', user['phone'])
        
        # Save to database
        save_user(user)
        
        # Send notification
        send_notification(user['email'], 'Profile updated')
        
        # Log action
        log_action(user['id'], 'profile_update')
        
        return user
    elif request_data['action'] == 'delete_account':
        # Delete account logic
        delete_user(user['id'])
        send_notification(user['email'], 'Account deleted')
        log_action(user['id'], 'account_deletion')
        return {'status': 'deleted'}
    else:
        return {'error': 'Unknown action'}

# Hardcoded secrets (security issue)
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# Poor naming conventions
def calc(x, y):
    return x + y

# No documentation
def mysterious_function(a, b, c):
    temp = a * 2
    if b > 10:
        temp += c
    else:
        temp -= c
    return temp ** 2

# Resource leak - file not closed properly
def read_large_file(filepath):
    f = open(filepath, 'r')
    content = f.read()
    # File never closed!
    return content

# Inefficient code
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j]:
                if items[i] not in duplicates:
                    duplicates.append(items[i])
    return duplicates

# No input validation
def divide_numbers(a, b):
    return a / b  # What if b is 0?

# Overly nested code
def complex_logic(data):
    if data:
        if isinstance(data, dict):
            if 'items' in data:
                if data['items']:
                    if len(data['items']) > 0:
                        for item in data['items']:
                            if item:
                                if 'value' in item:
                                    if item['value'] > 0:
                                        return item['value']
    return None

# Unused imports and variables
import sys
import datetime
unused_variable = "This is never used"

# Poor exception handling
def risky_operation():
    try:
        result = dangerous_function()
        return result
    except:
        pass  # Silently ignoring all exceptions

# Magic numbers
def calculate_discount(price):
    if price > 100:
        return price * 0.15  # What does 0.15 represent?
    elif price > 50:
        return price * 0.10  # What does 0.10 represent?
    else:
        return price * 0.05  # What does 0.05 represent?

# Missing type hints
def format_user_data(user):
    return {
        'id': user['id'],
        'name': user['name'].title(),
        'email': user['email'].lower(),
        'created': user['created_at']
    }

# Placeholder functions for the example
def validate_data(data):
    pass

def execute_query(query):
    pass

def save_user(user):
    pass

def send_notification(email, message):
    pass

def log_action(user_id, action):
    pass

def delete_user(user_id):
    pass

def dangerous_function():
    pass
