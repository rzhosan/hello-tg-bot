#!/usr/bin/env python3
import pickle
from datetime import date

USER_ID = 1958871862
SPINS_TO_ADD = 5

try:
    # Load current data
    with open('bot_data.pkl', 'rb') as f:
        data = pickle.load(f)
    
    print(f"=== Adding {SPINS_TO_ADD} spins to User ID: {USER_ID} ===")
    
    if 'user_data' not in data:
        data['user_data'] = {}
    
    if USER_ID not in data['user_data']:
        data['user_data'][USER_ID] = {}
    
    user_data = data['user_data'][USER_ID]
    
    # Show before
    print(f"Before: spin_uses = {user_data.get('spin_uses', 'NOT SET')}")
    
    # Initialize if needed
    if 'spin_uses' not in user_data:
        user_data['spin_uses'] = 0
        user_data['spin_date'] = str(date.today())
    
    # Add spins
    user_data['spin_uses'] += SPINS_TO_ADD
    
    # Show after
    print(f"After: spin_uses = {user_data['spin_uses']}")
    
    # Save back
    with open('bot_data.pkl', 'wb') as f:
        pickle.dump(data, f)
    
    print(f"✅ Successfully added {SPINS_TO_ADD} spins!")
    print(f"Total spins now: {user_data['spin_uses']}")
    
except FileNotFoundError:
    print("❌ bot_data.pkl not found")
except Exception as e:
    print(f"❌ Error: {e}")
