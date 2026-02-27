#!/usr/bin/env python3
import pickle
import json

try:
    with open('bot_data.pkl', 'rb') as f:
        data = pickle.load(f)
    
    print("=== BOT DATA ===")
    print(f"Keys: {data.keys()}\n")
    
    if 'user_data' in data:
        user_data = data['user_data']
        print(f"Number of users: {len(user_data)}\n")
        
        for user_id, udata in user_data.items():
            print(f"\n--- User ID: {user_id} ---")
            print(f"Spin uses: {udata.get('spin_uses', 'NOT SET')}")
            print(f"Spin date: {udata.get('spin_date', 'NOT SET')}")
            print(f"Language: {udata.get('language', 'NOT SET')}")
            print(f"Bot blocked: {udata.get('bot_blocked', False)}")
            if 'last_payment_charge_id' in udata:
                print(f"Last payment charge ID: {udata['last_payment_charge_id']}")
            print(f"All keys: {list(udata.keys())}")
    else:
        print("No user_data found in pickle file")
        
except FileNotFoundError:
    print("bot_data.pkl not found")
except Exception as e:
    print(f"Error reading pickle file: {e}")
