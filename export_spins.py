#!/usr/bin/env python3
import pickle
import json
from datetime import datetime

try:
    # Load bot data
    with open('bot_data.pkl', 'rb') as f:
        data = pickle.load(f)
    
    users_info = []
    
    if 'user_data' in data:
        for user_id, user_data in data['user_data'].items():
            user_info = {
                'user_id': user_id,
                'spin_uses': user_data.get('spin_uses', 0),
                'spin_date': user_data.get('spin_date', 'nie ustawiona'),
                'language': user_data.get('language', 'nie wybrano'),
                'bot_blocked': user_data.get('bot_blocked', False)
            }
            users_info.append(user_info)
    
    # Sort by spin_uses descending
    users_info.sort(key=lambda x: x['spin_uses'], reverse=True)
    
    # Save to JSON
    output = {
        'export_date': datetime.now().isoformat(),
        'total_users': len(users_info),
        'users': users_info
    }
    
    with open('users_spins.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Also create readable text file
    with open('users_spins.txt', 'w', encoding='utf-8') as f:
        f.write("=== INFORMACJE O SPINACH UŻYTKOWNIKÓW ===\n")
        f.write(f"Data wyeksportowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Liczba użytkowników: {len(users_info)}\n\n")
        
        for user in users_info:
            f.write(f"User ID: {user['user_id']}\n")
            f.write(f"  Spiny: {user['spin_uses']}\n")
            f.write(f"  Data ostatniego spinu: {user['spin_date']}\n")
            f.write(f"  Język: {user['language']}\n")
            f.write(f"  Bot zablokowany: {'Tak' if user['bot_blocked'] else 'Nie'}\n")
            f.write("\n")
    
    print(f"✅ Wyeksportowano dane {len(users_info)} użytkowników")
    print(f"   Pliki: users_spins.json i users_spins.txt")
    
except Exception as e:
    print(f"❌ Błąd: {e}")
