import sqlite3
import json
import urllib.request
import os

print("Testing CDB download to memory...")
try:
    req = urllib.request.Request("https://raw.githubusercontent.com/salix5/cdb/gh-pages/cards.cdb", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        db_data = response.read()
    
    # Write to a temporary file first because sqlite3 python module can't directly load bytes into :memory: without a disk file first using backup API or similar
    with open('/tmp/temp_cards.cdb', 'wb') as f:
        f.write(db_data)
        
    source_db = sqlite3.connect('/tmp/temp_cards.cdb')
    mem_db = sqlite3.connect(':memory:')
    source_db.backup(mem_db)
    source_db.close()
    os.remove('/tmp/temp_cards.cdb')
    
    cursor = mem_db.cursor()
    cursor.execute("SELECT texts.id, texts.name, datas.alias FROM texts JOIN datas ON texts.id = datas.id LIMIT 5")
    print(cursor.fetchall())
    print("Success loading CDB to memory!")
    mem_db.close()
except Exception as e:
    print(f"Error: {e}")

print("\nTesting cid_table download...")
try:
    req = urllib.request.Request("https://raw.githubusercontent.com/salix5/salix5.github.io/master/query/text/cid_table.json", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        cid_data = json.loads(response.read().decode('utf-8'))
    print(f"Loaded {len(cid_data)} entries from cid_table.json")
    # Show first 3 items
    print(list(cid_data.items())[:3])
except Exception as e:
    print(f"Error loading cid_table.json: {e}")
