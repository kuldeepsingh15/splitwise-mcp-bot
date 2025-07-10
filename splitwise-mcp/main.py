import os
from fastmcp import FastMCP
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mcp = FastMCP(
    name="Splitwise MCP Server", 
    instructions="""You are a helpful assistant that can interact with the Splitwise API to manage users, groups, friends, expenses, and more. 

Splitwise is a popular expense-sharing app that helps people split bills and track shared expenses. This MCP server provides tools to:

- Manage user profiles and account settings
- Create and manage groups for shared expenses (e.g., roommates, trips, couples)
- Add and manage friends for individual expense sharing
- Create, update, and delete expenses with various splitting options
- Add comments to expenses for better communication
- Get notifications about account activity
- Retrieve supported currencies and expense categories

The API uses a personal access token for authentication and supports both equal splits and custom share-based expense splitting."""
)

# Get configuration from environment variables
base_url = os.getenv("SPLITWISE_BASE_URL", "https://secure.splitwise.com/api/v3.0")
personal_access_token = os.getenv("SPLITWISE_API_TOKEN")

if not personal_access_token:
    raise ValueError("SPLITWISE_API_TOKEN environment variable is required")

def get_headers():
    return {
        "Authorization": f"Bearer {personal_access_token}"
    }

# User endpoints
@mcp.tool
def get_current_user() -> dict:
    """Retrieve detailed information about the currently authenticated user's profile.
    
    This tool fetches the complete user profile including:
    - Personal information (name, email, registration status)
    - Profile picture URLs (small, medium, large sizes)
    - Notification settings and unread notification count
    - Default currency and locale preferences
    - Account creation and last activity timestamps
    
    Returns:
        dict: Complete user profile with all account details and preferences
        
    Example response includes user ID, name, email, notification count, default currency, etc.
    """
    print("Getting current user")
    headers = get_headers()
    response = requests.get(f"{base_url}/get_current_user", headers=headers)
    return response.json()

@mcp.tool
def get_user(user_id: int) -> dict:
    """Retrieve public profile information about another Splitwise user by their ID.
    
    This tool allows you to view another user's public profile information. You can only
    access users who are your friends or in groups with you.
    
    Args:
        user_id (int): The unique identifier of the user whose profile you want to retrieve
        
    Returns:
        dict: Public profile information including name, email, profile picture, and registration status
        
    Note: This will only work for users who are your friends or in shared groups with you.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_user/{user_id}", headers=headers)
    return response.json()

@mcp.tool
def update_user(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    locale: Optional[str] = None,
    default_currency: str = "INR"
) -> dict:
    """Update the current user's profile information and account settings.
    
    This tool allows you to modify various aspects of your Splitwise account:
    - Personal details (name, email)
    - Account security (password)
    - Regional preferences (locale, default currency)
    
    Only provide the parameters you want to change - unchanged parameters will keep their current values.
    
    Args:
        user_id (int): Your user ID (must be your own ID)
        first_name (str, optional): New first name for your profile
        last_name (str, optional): New last name for your profile
        email (str, optional): New email address for your account
        password (str, optional): New password for your account
        locale (str, optional): New locale setting (e.g., 'en', 'es', 'fr')
        default_currency (str, optional): New default currency code (e.g., 'USD', 'EUR', 'INR')
        
    Returns:
        dict: Updated user profile information
        
    Examples:
        - Update just your name: update_user(123, first_name="John", last_name="Doe")
        - Change default currency: update_user(123, default_currency="USD")
        - Update multiple fields: update_user(123, first_name="Jane", email="jane@example.com", default_currency="EUR")
    """
    headers = get_headers()
    data = {}
    
    if first_name is not None:
        data['first_name'] = first_name
    if last_name is not None:
        data['last_name'] = last_name
    if email is not None:
        data['email'] = email
    if password is not None:
        data['password'] = password
    if locale is not None:
        data['locale'] = locale
    if default_currency is not None:
        data['default_currency'] = default_currency
    
    response = requests.post(f"{base_url}/update_user/{user_id}", headers=headers, json=data)
    return response.json()

# Group endpoints
@mcp.tool
def get_groups() -> dict:
    """Retrieve all groups that the current user is a member of.
    
    This tool returns a comprehensive list of all groups you belong to, including:
    - Group details (name, type, creation date)
    - Member information and balances
    - Group avatars and cover photos
    - Debt information (original and simplified)
    - Group settings like debt simplification preferences
    
    Groups can be of various types: home (roommates), trip, couple, apartment, house, or other.
    Expenses not associated with any group are listed under group ID 0.
    
    Returns:
        dict: List of all user's groups with detailed information about each group
        
    Example: Returns groups like "Apartment 2024", "Weekend Trip", "Couple Expenses", etc.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_groups", headers=headers)
    return response.json()

@mcp.tool
def get_group(group_id: int) -> dict:
    """Get detailed information about a specific group by its ID.
    
    This tool provides comprehensive details about a particular group including:
    - Complete group information (name, type, settings)
    - All group members with their current balances
    - Group avatar and cover photo URLs
    - Original and simplified debt information
    - Group invite link for adding new members
    
    Args:
        group_id (int): The unique identifier of the group to retrieve
        
    Returns:
        dict: Detailed group information including members, balances, and settings
        
    Note: You can only access groups where you are a member.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_group/{group_id}", headers=headers)
    return response.json()

@mcp.tool
def create_group(
    name: str,
    group_type: str = "other",
    simplify_by_default: bool = False,
    users: Optional[List[Dict[str, str]]] = None
) -> dict:
    """Create a new group for sharing expenses with other users.
    
    This tool creates a new group and automatically adds you as a member. Groups are
    the primary way to organize shared expenses in Splitwise.
    
    Group types determine the default avatar and help categorize the group's purpose:
    - "home": Roommates or household expenses
    - "trip": Travel and vacation expenses
    - "couple": Romantic partner expenses
    - "apartment": Apartment-specific expenses
    - "house": House-specific expenses
    - "other": General purpose group
    
    Args:
        name (str): The name of the group (e.g., "Apartment 2024", "Weekend Trip")
        group_type (str, optional): Type of group - "home", "trip", "couple", "other", "apartment", "house"
        simplify_by_default (bool, optional): Whether to automatically simplify debts in this group
        users (list, optional): List of users to add to the group. Each user dict should contain:
            - "first_name": User's first name
            - "last_name": User's last name  
            - "email": User's email address
            - "user_id": User's ID (if known)
            
    Returns:
        dict: Created group information with group ID and member details
        
    Examples:
        - Create a roommate group: create_group("Apartment 2024", "home", True)
        - Create a trip group with members: create_group("Weekend Trip", "trip", users=[{"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"}])
    """
    headers = get_headers()
    data = {
        "name": name,
        "group_type": group_type,
        "simplify_by_default": simplify_by_default
    }
    
    # Add users if provided
    if users:
        for i, user in enumerate(users):
            for key, value in user.items():
                data[f"users__{i}__{key}"] = value
    
    response = requests.post(f"{base_url}/create_group", headers=headers, json=data)
    return response.json()

@mcp.tool
def delete_group(group_id: int) -> dict:
    """Permanently delete a group and all associated data.
    
    This action is irreversible and will delete:
    - The group itself
    - All expenses in the group
    - All comments on those expenses
    - All member relationships within the group
    
    Use this tool carefully as it cannot be undone without using the undelete_group tool.
    
    Args:
        group_id (int): The unique identifier of the group to delete
        
    Returns:
        dict: Success status of the deletion operation
        
    Warning: This permanently removes all group data and cannot be undone easily.
    """
    headers = get_headers()
    response = requests.post(f"{base_url}/delete_group/{group_id}", headers=headers)
    return response.json()

@mcp.tool
def undelete_group(group_id: int) -> dict:
    """Restore a previously deleted group and its associated data.
    
    This tool attempts to restore a group that was previously deleted. The success
    depends on whether the group can still be restored and your permissions.
    
    Args:
        group_id (int): The unique identifier of the deleted group to restore
        
    Returns:
        dict: Success status and any error messages from the restoration attempt
        
    Note: Restoration may not always be possible depending on how long ago the group was deleted.
    """
    headers = get_headers()
    response = requests.post(f"{base_url}/undelete_group/{group_id}", headers=headers)
    return response.json()

@mcp.tool
def add_user_to_group(
    group_id: int,
    user_id: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None
) -> dict:
    """Add a user to an existing group for expense sharing.
    
    This tool allows you to invite someone to join a group. You can add users in two ways:
    1. By providing their user ID (if you know it)
    2. By providing their name and email (creates account if they don't exist)
    
    The user will receive an invitation to join the group.
    
    Args:
        group_id (int): The unique identifier of the group to add the user to
        user_id (int, optional): The ID of an existing Splitwise user
        first_name (str, optional): First name of the user (required if user_id not provided)
        last_name (str, optional): Last name of the user (required if user_id not provided)
        email (str, optional): Email address of the user (required if user_id not provided)
        
    Returns:
        dict: Success status and user information
        
    Examples:
        - Add by user ID: add_user_to_group(123, user_id=456)
        - Add by email: add_user_to_group(123, first_name="John", last_name="Doe", email="john@example.com")
        
    Note: Either user_id OR all of first_name, last_name, and email must be provided.
    """
    headers = get_headers()
    data: Dict[str, Any] = {"group_id": group_id}
    
    if user_id is not None:
        data["user_id"] = user_id
    else:
        if first_name is None or last_name is None or email is None:
            raise ValueError("Either user_id or all of first_name, last_name, and email must be provided")
        data["first_name"] = first_name
        data["last_name"] = last_name
        data["email"] = email
    
    response = requests.post(f"{base_url}/add_user_to_group", headers=headers, json=data)
    return response.json()

@mcp.tool
def remove_user_from_group(group_id: int, user_id: int) -> dict:
    """Remove a user from a group.
    
    This tool removes a user from a group. The operation will fail if the user
    has a non-zero balance in the group (they owe money or are owed money).
    
    Args:
        group_id (int): The unique identifier of the group
        user_id (int): The unique identifier of the user to remove
        
    Returns:
        dict: Success status and any error messages
        
    Note: Users with outstanding balances cannot be removed from groups.
    """
    headers = get_headers()
    data = {
        "group_id": group_id,
        "user_id": user_id
    }
    response = requests.post(f"{base_url}/remove_user_from_group", headers=headers, json=data)
    return response.json()

# Friend endpoints
@mcp.tool
def get_friends() -> dict:
    """Retrieve all friends of the current user.
    
    This tool returns a list of all your Splitwise friends with detailed information:
    - Friend profile information (name, email, profile picture)
    - Current balance with each friend
    - Group balances with each friend
    - Last activity timestamps
    
    Friends are users you can share individual expenses with outside of groups.
    
    Returns:
        dict: List of all friends with balance and relationship information
        
    Example: Returns friends like "Alice Smith", "Bob Johnson" with their current balances.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_friends", headers=headers)
    return response.json()

@mcp.tool
def get_friend(friend_id: int) -> dict:
    """Get detailed information about a specific friend.
    
    This tool provides comprehensive details about a particular friend including:
    - Complete profile information
    - Current balance between you and the friend
    - Group balances with the friend
    - Relationship timestamps
    
    Args:
        friend_id (int): The unique identifier of the friend to retrieve
        
    Returns:
        dict: Detailed friend information including balances and relationship details
        
    Note: You can only access information about users who are your friends.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_friend/{friend_id}", headers=headers)
    return response.json()

@mcp.tool
def create_friend(
    user_email: str,
    user_first_name: Optional[str] = None,
    user_last_name: Optional[str] = None
) -> dict:
    """Add a new friend to your Splitwise account.
    
    This tool creates a friendship with another user. If the user doesn't exist on Splitwise,
    you must provide their first name to create their account. If they already exist,
    the name parameters will be ignored.
    
    Once added as a friend, you can share individual expenses with them outside of groups.
    
    Args:
        user_email (str): Email address of the user to add as a friend
        user_first_name (str, optional): First name (required if user doesn't exist on Splitwise)
        user_last_name (str, optional): Last name (required if user doesn't exist on Splitwise)
        
    Returns:
        dict: Friend information including profile details and relationship status
        
    Examples:
        - Add existing user: create_friend("alice@example.com")
        - Add new user: create_friend("bob@example.com", "Bob", "Johnson")
        
    Note: If the user doesn't exist, you must provide both first_name and last_name.
    """
    headers = get_headers()
    data = {"user_email": user_email}
    
    if user_first_name is not None:
        data["user_first_name"] = user_first_name
    if user_last_name is not None:
        data["user_last_name"] = user_last_name
    
    response = requests.post(f"{base_url}/create_friend", headers=headers, json=data)
    return response.json()

@mcp.tool
def create_friends(friends: List[Dict[str, str]]) -> dict:
    """Add multiple friends to your Splitwise account at once.
    
    This tool allows you to add several friends simultaneously, which is more efficient
    than adding them one by one. For each friend, provide their email and name if needed.
    
    Args:
        friends (list): List of friend dictionaries. Each dict should contain:
            - "email": Friend's email address (required)
            - "first_name": Friend's first name (required if user doesn't exist)
            - "last_name": Friend's last name (required if user doesn't exist)
            
    Returns:
        dict: List of created friends and any error messages for failed additions
        
    Examples:
        - Add multiple existing users: [{"email": "alice@example.com"}, {"email": "bob@example.com"}]
        - Add new users: [{"email": "charlie@example.com", "first_name": "Charlie", "last_name": "Brown"}]
    """
    headers = get_headers()
    data = {}
    
    for i, friend in enumerate(friends):
        for key, value in friend.items():
            data[f"friends__{i}__{key}"] = value
    
    response = requests.post(f"{base_url}/create_friends", headers=headers, json=data)
    return response.json()

@mcp.tool
def delete_friend(friend_id: int) -> dict:
    """Remove a friendship from your Splitwise account.
    
    This tool ends the friendship with another user. This will remove them from your
    friends list and you won't be able to share individual expenses with them anymore.
    
    Args:
        friend_id (int): The unique identifier of the friend to remove
        
    Returns:
        dict: Success status and any error messages from the friendship removal
        
    Note: This action cannot be undone - you'll need to add them as a friend again if needed.
    """
    headers = get_headers()
    response = requests.post(f"{base_url}/delete_friend/{friend_id}", headers=headers)
    return response.json()

# Expense endpoints
@mcp.tool
def get_expense(expense_id: int) -> dict:
    """Retrieve detailed information about a specific expense.
    
    This tool provides comprehensive details about an expense including:
    - Complete expense information (description, cost, date, category)
    - How the expense was split among users
    - Payment and owed amounts for each person
    - Comments and receipts
    - Creation and modification timestamps
    
    Args:
        expense_id (int): The unique identifier of the expense to retrieve
        
    Returns:
        dict: Complete expense details including splits, comments, and metadata
        
    Note: You can only access expenses that involve you (you're a member of the group or friend).
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_expense/{expense_id}", headers=headers)
    return response.json()

@mcp.tool
def get_expenses(
    group_id: Optional[int] = None,
    friend_id: Optional[int] = None,
    dated_after: Optional[str] = None,
    dated_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> dict:
    """Retrieve a list of expenses with optional filtering and pagination.
    
    This tool returns expenses that involve the current user, with powerful filtering options:
    - Filter by group or friend
    - Filter by date ranges (when expense occurred or was last updated)
    - Pagination support for large expense lists
    
    Args:
        group_id (int, optional): Filter expenses to only those in this specific group
        friend_id (int, optional): Filter expenses to only those with this specific friend
        dated_after (str, optional): Filter expenses dated after this date (ISO format: "2024-01-01T00:00:00Z")
        dated_before (str, optional): Filter expenses dated before this date (ISO format: "2024-12-31T23:59:59Z")
        updated_after (str, optional): Filter expenses updated after this date (ISO format)
        updated_before (str, optional): Filter expenses updated before this date (ISO format)
        limit (int, optional): Maximum number of expenses to return (default: 20, max: 1000)
        offset (int, optional): Number of expenses to skip for pagination (default: 0)
        
    Returns:
        dict: List of expenses matching the filter criteria
        
    Examples:
        - Get all expenses: get_expenses()
        - Get recent expenses: get_expenses(dated_after="2024-01-01T00:00:00Z")
        - Get group expenses: get_expenses(group_id=123)
        - Get friend expenses: get_expenses(friend_id=456)
        - Paginated results: get_expenses(limit=10, offset=20)
        
    Note: If both group_id and friend_id are provided, group_id takes precedence.
    """
    headers = get_headers()
    params = {}
    
    if group_id is not None:
        params['group_id'] = group_id
    if friend_id is not None:
        params['friend_id'] = friend_id
    if dated_after is not None:
        params['dated_after'] = dated_after
    if dated_before is not None:
        params['dated_before'] = dated_before
    if updated_after is not None:
        params['updated_after'] = updated_after
    if updated_before is not None:
        params['updated_before'] = updated_before
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    
    response = requests.get(f"{base_url}/get_expenses", headers=headers, params=params)
    return response.json()

@mcp.tool
def create_expense_equal_split(
    description: str,
    cost: str,
    group_id: int,
    currency_code: str = "INR",
    date: Optional[str] = None,
    details: Optional[str] = None,
    category_id: Optional[int] = None,
    repeat_interval: str = "never"
) -> dict:
    """Create an expense that is split equally among all group members.
    
    This tool creates a new expense where the total cost is divided equally among
    all members of the specified group. The current user is automatically set as
    the person who paid for the expense.
    
    Args:
        description (str): Short description of the expense (e.g., "Grocery shopping", "Dinner")
        cost (str): Total cost of the expense as a string (e.g., "25.50", "100.00")
        group_id (int): ID of the group to create the expense in
        currency_code (str, optional): Currency code (e.g., "USD", "EUR", "INR"). Default: "INR"
        date (str, optional): Date when the expense occurred (ISO format: "2024-01-15T12:00:00Z")
        details (str, optional): Additional notes or details about the expense
        category_id (int, optional): ID of the expense category (get from get_categories())
        repeat_interval (str, optional): How often to repeat this expense - "never", "weekly", "fortnightly", "monthly", "yearly"
        
    Returns:
        dict: Created expense information with split details
        
    Examples:
        - Simple expense: create_expense_equal_split("Pizza", "30.00", 123)
        - Detailed expense: create_expense_equal_split("Rent", "1200.00", 123, "USD", "2024-01-01T00:00:00Z", "Monthly rent payment", 15, "monthly")
        
    Note: The expense will be split equally among all group members, with you as the payer.
    """
    headers = get_headers()
    data = {
        "description": description,
        "cost": cost,
        "group_id": group_id,
        "split_equally": True,
        "currency_code": currency_code,
        "repeat_interval": repeat_interval
    }
    
    if date is not None:
        data["date"] = date
    if details is not None:
        data["details"] = details
    if category_id is not None:
        data["category_id"] = category_id
    
    response = requests.post(f"{base_url}/create_expense", headers=headers, json=data)
    return response.json()

@mcp.tool
def create_expense_by_shares(
    description: str,
    cost: str,
    group_id: int,
    users: List[Dict[str, str]],
    currency_code: str = "INR",
    date: Optional[str] = None,
    details: Optional[str] = None,
    category_id: Optional[int] = None,
    repeat_interval: str = "never"
) -> dict:
    """Create an expense with custom payment and owed amounts for each person.
    
    This tool creates a new expense with precise control over how much each person
    paid and how much they owe. This is useful for complex splitting scenarios
    where people paid different amounts or owe different portions.
    
    Each user in the users list must specify:
    - How much they paid (paid_share)
    - How much they owe (owed_share)
    - Their identification (user_id OR email + first_name + last_name)
    
    Args:
        description (str): Short description of the expense (e.g., "Concert tickets", "Hotel booking")
        cost (str): Total cost of the expense as a string (e.g., "150.00", "75.50")
        group_id (int): ID of the group (use 0 for no group - individual expense)
        users (list): List of user dictionaries. Each dict should contain:
            - "user_id" OR ("email", "first_name", "last_name"): User identification
            - "paid_share": Amount this user paid (e.g., "50.00", "0.00")
            - "owed_share": Amount this user owes (e.g., "25.00", "15.00")
        currency_code (str, optional): Currency code (e.g., "USD", "EUR", "INR"). Default: "INR"
        date (str, optional): Date when the expense occurred (ISO format: "2024-01-15T12:00:00Z")
        details (str, optional): Additional notes or details about the expense
        category_id (int, optional): ID of the expense category (get from get_categories())
        repeat_interval (str, optional): How often to repeat this expense - "never", "weekly", "fortnightly", "monthly", "yearly"
        
    Returns:
        dict: Created expense information with custom split details
        
    Examples:
        - Group expense with custom splits: users=[{"user_id": 123, "paid_share": "100.00", "owed_share": "50.00"}, {"user_id": 456, "paid_share": "0.00", "owed_share": "50.00"}]
        - Individual expense: users=[{"email": "alice@example.com", "first_name": "Alice", "last_name": "Smith", "paid_share": "30.00", "owed_share": "15.00"}]
        
    Note: The sum of paid_shares should equal the total cost, and the sum of owed_shares should equal the total cost.
    """
    headers = get_headers()
    data = {
        "description": description,
        "cost": cost,
        "group_id": group_id,
        "currency_code": currency_code,
        "repeat_interval": repeat_interval
    }
    
    if date is not None:
        data["date"] = date
    if details is not None:
        data["details"] = details
    if category_id is not None:
        data["category_id"] = category_id
    
    # Add user shares
    for i, user in enumerate(users):
        for key, value in user.items():
            data[f"users__{i}__{key}"] = value
    
    response = requests.post(f"{base_url}/create_expense", headers=headers, json=data)
    return response.json()

@mcp.tool
def update_expense(
    expense_id: int,
    description: Optional[str] = None,
    cost: Optional[str] = None,
    group_id: Optional[int] = None,
    currency_code: str = "INR",
    date: Optional[str] = None,
    details: Optional[str] = None,
    category_id: Optional[int] = None,
    repeat_interval: Optional[str] = None,
    users: Optional[List[Dict[str, str]]] = None
) -> dict:
    """Update an existing expense with new information.
    
    This tool allows you to modify any aspect of an existing expense. Only provide
    the parameters you want to change - unchanged parameters will keep their current values.
    
    If you provide new user shares, ALL existing shares will be replaced with the new ones.
    
    Args:
        expense_id (int): The unique identifier of the expense to update
        description (str, optional): New description for the expense
        cost (str, optional): New total cost as a string (e.g., "25.50")
        group_id (int, optional): New group ID (use 0 for no group)
        currency_code (str, optional): New currency code (e.g., "USD", "EUR", "INR")
        date (str, optional): New date when the expense occurred (ISO format)
        details (str, optional): New notes or details about the expense
        category_id (int, optional): New category ID (get from get_categories())
        repeat_interval (str, optional): New repeat interval - "never", "weekly", "fortnightly", "monthly", "yearly"
        users (list, optional): New user shares. If provided, replaces ALL existing shares. Each dict should contain:
            - "user_id" OR ("email", "first_name", "last_name"): User identification
            - "paid_share": Amount this user paid
            - "owed_share": Amount this user owes
            
    Returns:
        dict: Updated expense information
        
    Examples:
        - Update description: update_expense(123, description="Updated description")
        - Update cost: update_expense(123, cost="35.00")
        - Update splits: update_expense(123, users=[{"user_id": 456, "paid_share": "20.00", "owed_share": "10.00"}])
        
    Note: Only provide the parameters you want to change. If you provide users, all existing shares will be replaced.
    """
    headers = get_headers()
    data = {}
    
    if description is not None:
        data["description"] = description
    if cost is not None:
        data["cost"] = cost
    if group_id is not None:
        data["group_id"] = group_id
    if currency_code is not None:
        data["currency_code"] = currency_code
    if date is not None:
        data["date"] = date
    if details is not None:
        data["details"] = details
    if category_id is not None:
        data["category_id"] = category_id
    if repeat_interval is not None:
        data["repeat_interval"] = repeat_interval
    
    # Add user shares if provided
    if users is not None:
        for i, user in enumerate(users):
            for key, value in user.items():
                data[f"users__{i}__{key}"] = value
    
    response = requests.post(f"{base_url}/update_expense/{expense_id}", headers=headers, json=data)
    return response.json()

@mcp.tool
def delete_expense(expense_id: int) -> dict:
    """Delete an expense from your Splitwise account.
    
    This tool removes an expense and all its associated data including:
    - The expense record itself
    - All comments on the expense
    - Receipt images
    - Split information
    
    The expense will be moved to a deleted state but can potentially be restored
    using the undelete_expense tool.
    
    Args:
        expense_id (int): The unique identifier of the expense to delete
        
    Returns:
        dict: Success status and any error messages from the deletion
        
    Note: This action can be undone using the undelete_expense tool.
    """
    headers = get_headers()
    response = requests.post(f"{base_url}/delete_expense/{expense_id}", headers=headers)
    return response.json()

@mcp.tool
def undelete_expense(expense_id: int) -> dict:
    """Restore a previously deleted expense.
    
    This tool attempts to restore an expense that was previously deleted. The success
    depends on whether the expense can still be restored and your permissions.
    
    Args:
        expense_id (int): The unique identifier of the deleted expense to restore
        
    Returns:
        dict: Success status and any error messages from the restoration attempt
        
    Note: Restoration may not always be possible depending on how long ago the expense was deleted.
    """
    headers = get_headers()
    response = requests.post(f"{base_url}/undelete_expense/{expense_id}", headers=headers)
    return response.json()

# Comment endpoints
@mcp.tool
def get_comments(expense_id: int) -> dict:
    """Retrieve all comments for a specific expense.
    
    This tool returns all comments associated with an expense, including:
    - Comment content and timestamps
    - User information for each comment
    - Comment types (user comments vs system comments)
    
    Comments are useful for discussing expenses, asking questions, or providing context.
    
    Args:
        expense_id (int): The unique identifier of the expense to get comments for
        
    Returns:
        dict: List of all comments for the expense with user and timestamp information
        
    Note: You can only access comments for expenses that involve you.
    """
    headers = get_headers()
    params = {'expense_id': expense_id}
    response = requests.get(f"{base_url}/get_comments", headers=headers, params=params)
    return response.json()

@mcp.tool
def create_comment(expense_id: int, content: str) -> dict:
    """Add a comment to an expense for discussion or clarification.
    
    This tool allows you to add a comment to an expense to discuss details,
    ask questions, or provide additional context about the expense.
    
    Comments are visible to all users involved in the expense and can help
    clarify splitting decisions or provide important context.
    
    Args:
        expense_id (int): The unique identifier of the expense to comment on
        content (str): The comment text to add (e.g., "Does this include tip?", "Split the delivery fee too")
        
    Returns:
        dict: Created comment information including user and timestamp details
        
    Examples:
        - Simple comment: create_comment(123, "Does this include the delivery fee?")
        - Clarification: create_comment(123, "I paid for the parking separately, so we can ignore that cost")
        
    Note: Comments are visible to all users involved in the expense.
    """
    headers = get_headers()
    data = {
        "expense_id": expense_id,
        "content": content
    }
    response = requests.post(f"{base_url}/create_comment", headers=headers, json=data)
    return response.json()

@mcp.tool
def delete_comment(comment_id: int) -> dict:
    """Delete a comment from an expense.
    
    This tool removes a comment that you previously added to an expense.
    You can only delete comments that you created.
    
    Args:
        comment_id (int): The unique identifier of the comment to delete
        
    Returns:
        dict: Deleted comment information
        
    Note: You can only delete comments that you created. Comments by other users cannot be deleted.
    """
    headers = get_headers()
    response = requests.post(f"{base_url}/delete_comment/{comment_id}", headers=headers)
    return response.json()

# Notification endpoints
@mcp.tool
def get_notifications(
    updated_after: Optional[str] = None,
    limit: Optional[int] = None
) -> dict:
    """Retrieve recent activity notifications for your Splitwise account.
    
    This tool returns a list of recent notifications about activity on your account,
    such as new expenses, comments, group changes, and friend requests.
    
    Notification types include:
    - 0: Expense added
    - 1: Expense updated  
    - 2: Expense deleted
    - 3: Comment added
    - 4: Added to group
    - 5: Removed from group
    - 6: Group deleted
    - 7: Group settings changed
    - 8: Added as friend
    - 9: Removed as friend
    - 10: News
    - 11: Debt simplification
    - 12: Group undeleted
    - 13: Expense undeleted
    - 14: Group currency conversion
    - 15: Friend currency conversion
    
    Args:
        updated_after (str, optional): Filter notifications updated after this date (ISO format: "2024-01-01T00:00:00Z")
        limit (int, optional): Maximum number of notifications to return (0 for maximum)
        
    Returns:
        dict: List of recent notifications with activity details and timestamps
        
    Examples:
        - Get all notifications: get_notifications()
        - Get recent notifications: get_notifications(updated_after="2024-01-01T00:00:00Z")
        - Limit results: get_notifications(limit=10)
        
    Note: The content field contains HTML-formatted text suitable for display.
    """
    headers = get_headers()
    params = {}
    
    if updated_after is not None:
        params['updated_after'] = updated_after
    if limit is not None:
        params['limit'] = limit
    
    response = requests.get(f"{base_url}/get_notifications", headers=headers, params=params)
    return response.json()

# Other endpoints
@mcp.tool
def get_currencies() -> dict:
    """Retrieve all supported currencies for expenses.
    
    This tool returns a comprehensive list of all currencies supported by Splitwise,
    including both official ISO 4217 codes and some unofficial codes (like BTC for Bitcoin).
    
    Each currency includes:
    - Currency code (e.g., "USD", "EUR", "INR")
    - Currency symbol/unit (e.g., "$", "€", "₹")
    
    Returns:
        dict: List of all supported currencies with their codes and symbols
        
    Example: Returns currencies like USD ($), EUR (€), INR (₹), GBP (£), etc.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_currencies", headers=headers)
    return response.json()

@mcp.tool
def get_categories() -> dict:
    """Retrieve all supported expense categories for organizing expenses.
    
    This tool returns a hierarchical list of all expense categories supported by Splitwise.
    Categories are organized into parent categories with subcategories for more specific classification.
    
    When creating expenses, you must use a subcategory ID, not a parent category ID.
    If you want to use a parent category without a specific subcategory, use the "Other" subcategory.
    
    Category structure includes:
    - Parent categories (e.g., "Food & Drink", "Transportation", "Utilities")
    - Subcategories (e.g., "Groceries", "Restaurants", "Gas", "Electricity")
    - Category IDs for use in expense creation
    - Category icons and display names
    
    Returns:
        dict: Hierarchical list of all expense categories with parent and subcategory information
        
    Example: Returns categories like Food & Drink > Groceries, Transportation > Gas, etc.
    """
    headers = get_headers()
    response = requests.get(f"{base_url}/get_categories", headers=headers)
    return response.json()

# Legacy tool for backward compatibility
@mcp.tool
def greet(name: str) -> str:
    """Simple greeting tool for testing the MCP server connection.
    
    This is a legacy tool maintained for backward compatibility and testing purposes.
    
    Args:
        name (str): Name to greet
        
    Returns:
        str: Greeting message
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=4200,
        path="/mcp",
        log_level="debug",
    )