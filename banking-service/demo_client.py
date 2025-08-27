#!/usr/bin/env python3
"""
Demo client for Banking Service API

This script demonstrates the complete banking workflow:
1. User signup
2. Account creation (checking & savings)
3. Money deposit
4. Account-to-account transfer
5. Card issuance
6. Monthly statement generation

Run the banking service first:
    uvicorn app.main:app --reload

Then run this demo:
    python demo_client.py
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000/api/v1"


def signup_user(email: str, password: str, full_name: str = None) -> str:
    """Sign up a new user and return access token."""
    data = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=data)
    response.raise_for_status()
    return response.json()["access_token"]


def create_account(token: str, account_type: str = "checking") -> dict:
    """Create a new account."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"type": account_type}
    response = requests.post(f"{BASE_URL}/accounts", json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def deposit_money(token: str, account_id: int, amount_cents: int, description: str = None) -> dict:
    """Deposit money into account."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"amount_cents": amount_cents, "description": description}
    response = requests.post(f"{BASE_URL}/accounts/{account_id}/deposit", json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def list_accounts(token: str) -> list:
    """List all accounts for user."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/accounts", headers=headers)
    response.raise_for_status()
    return response.json()


def transfer_money(token: str, from_account_id: int, to_account_id: int, amount_cents: int, description: str = None) -> list:
    """Transfer money between accounts."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "amount_cents": amount_cents,
        "description": description
    }
    response = requests.post(f"{BASE_URL}/transfers", json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def issue_card(token: str, account_id: int, holder_name: str) -> dict:
    """Issue a payment card for account."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "account_id": account_id,
        "holder_name": holder_name,
        "exp_month": 12,
        "exp_year": 2027,
        "cvv": "123"
    }
    response = requests.post(f"{BASE_URL}/cards", json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def generate_statement(token: str, account_id: int, month: str) -> dict:
    """Generate monthly statement for account."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"month": month}
    response = requests.post(f"{BASE_URL}/statements/{account_id}", json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def print_json(data, title: str):
    """Pretty print JSON data with title."""
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, default=str))


def main():
    """Run the complete banking demo."""
    print("🏦 Banking Service Demo")
    print("======================")
    
    try:
        # 1. Sign up a new user
        print("\n1. Signing up user...")
        token = signup_user("demo@example.com", "demopassword", "Demo User")
        print("✅ User signed up successfully")
        
        # 2. Create checking and savings accounts
        print("\n2. Creating accounts...")
        checking_account = create_account(token, "checking")
        savings_account = create_account(token, "savings")
        
        checking_id = checking_account["id"]
        savings_id = savings_account["id"]
        
        print(f"✅ Created checking account (ID: {checking_id})")
        print(f"✅ Created savings account (ID: {savings_id})")
        
        # 3. Deposit money into checking account
        print("\n3. Depositing money...")
        deposit_tx = deposit_money(token, checking_id, 100000, "Initial deposit")
        print_json(deposit_tx, "Deposit Transaction")
        
        # 4. Check account balances
        print("\n4. Checking account balances...")
        accounts = list_accounts(token)
        print_json(accounts, "Account Balances")
        
        # 5. Transfer money from checking to savings
        print("\n5. Transferring money...")
        transfer_txs = transfer_money(token, checking_id, savings_id, 25000, "Transfer to savings")
        print_json(transfer_txs, "Transfer Transactions")
        
        # 6. Check balances after transfer
        print("\n6. Checking balances after transfer...")
        accounts = list_accounts(token)
        print_json(accounts, "Updated Account Balances")
        
        # 7. Issue a payment card
        print("\n7. Issuing payment card...")
        card = issue_card(token, checking_id, "Demo User")
        print_json(card, "Issued Card")
        
        # 8. Generate monthly statement
        print("\n8. Generating statement...")
        current_month = datetime.now().strftime("%Y-%m")
        statement = generate_statement(token, checking_id, current_month)
        print_json(statement, f"Statement for {current_month}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nSummary:")
        print(f"• Created 2 accounts")
        print(f"• Deposited $1,000.00")
        print(f"• Transferred $250.00 to savings")
        print(f"• Issued payment card")
        print(f"• Generated monthly statement")
        
    except requests.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        print("\n💡 Make sure the banking service is running:")
        print("   uvicorn app.main:app --reload")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
