"""
Database Verification Tool
Validates the SQLite database against bottle annotations to ensure all bottles have proper pricing
"""
import os
import sys
import sqlite3
import json
import pandas as pd

# Add the parent directory to the path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from modules import bottle_matcher

# Paths
DB_PATH = os.path.join(parent_dir, 'data', 'db', 'baxus.db')
BOTTLE_ANNOTATIONS_DIR = os.path.join(parent_dir, 'data', 'bottle_annotations')
OUTPUT_PATH = os.path.join(parent_dir, 'data', 'db', 'database_report.csv')

def get_all_annotations():
    """Get all bottle annotations from the annotations directory"""
    bottle_names = []
    
    if not os.path.exists(BOTTLE_ANNOTATIONS_DIR):
        print(f"Error: Bottle annotations directory not found: {BOTTLE_ANNOTATIONS_DIR}")
        return []
        
    for filename in os.listdir(BOTTLE_ANNOTATIONS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(BOTTLE_ANNOTATIONS_DIR, filename), 'r') as f:
                try:
                    data = json.load(f)
                    if 'name' in data:
                        bottle_names.append(data['name'])
                except:
                    print(f"Error reading {filename}")
                    continue
                    
    return bottle_names

def get_all_db_bottles():
    """Get all bottles from the SQLite database"""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found: {DB_PATH}")
        return []
        
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT name FROM whisky_bottles"
    df = pd.read_sql(query, conn)
    conn.close()
    
    return df['name'].tolist()

def check_bottle_pricing(bottle_name):
    """Check if a bottle has pricing data in the database"""
    if not os.path.exists(DB_PATH):
        return False
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Try exact match first
    query = "SELECT * FROM whisky_bottles WHERE name = ? LIMIT 1"
    cursor = conn.execute(query, (bottle_name,))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return True
        
    # Try case-insensitive match
    query = "SELECT * FROM whisky_bottles WHERE lower(name) = lower(?) LIMIT 1"
    cursor = conn.execute(query, (bottle_name,))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return True
        
    conn.close()
    return False

def main():
    print("\n========= WHISKY GOGGLES DATABASE VERIFICATION =========\n")
    
    # Get all bottle annotations and database entries
    annotation_bottles = get_all_annotations()
    db_bottles = get_all_db_bottles()
    
    print(f"Found {len(annotation_bottles)} bottles in annotations")
    print(f"Found {len(db_bottles)} bottles in SQLite database")
    
    # Check which annotations don't have matching database entries
    bottles_missing_pricing = []
    bottles_with_pricing = []
    
    total = len(annotation_bottles)
    for i, bottle in enumerate(annotation_bottles):
        print(f"Checking {i+1}/{total}: {bottle}", end="\r")
        
        # Check if this bottle has pricing data
        if check_bottle_pricing(bottle):
            bottles_with_pricing.append(bottle)
        else:
            # Try to match using our bottle matcher
            matched_name = bottle_matcher.match_bottle_name(bottle)
            if matched_name and matched_name != bottle and check_bottle_pricing(matched_name):
                bottles_with_pricing.append({
                    'annotation_name': bottle,
                    'matched_name': matched_name,
                    'status': 'matched'
                })
            else:
                bottles_missing_pricing.append({
                    'annotation_name': bottle,
                    'matched_name': matched_name if matched_name and matched_name != bottle else None,
                    'status': 'missing'
                })
                
    print("\n\n--- RESULTS ---")
    print(f"Total bottles: {total}")
    print(f"Bottles with direct pricing: {len([b for b in bottles_with_pricing if isinstance(b, str)])}")
    print(f"Bottles with matched pricing: {len([b for b in bottles_with_pricing if isinstance(b, dict)])}")
    print(f"Bottles missing pricing: {len(bottles_missing_pricing)}")
    
    # Generate CSV report
    if bottles_missing_pricing:
        print("\n--- BOTTLES MISSING PRICING ---")
        for i, bottle in enumerate(bottles_missing_pricing[:10]):  # Show first 10
            if isinstance(bottle, dict):
                print(f"{i+1}. {bottle['annotation_name']} (tried matching to: {bottle['matched_name']})")
            else:
                print(f"{i+1}. {bottle}")
                
        # Create report dataframe
        report_data = []
        for bottle in bottles_with_pricing:
            if isinstance(bottle, dict):
                report_data.append({
                    'annotation_name': bottle['annotation_name'],
                    'database_name': bottle['matched_name'],
                    'status': 'matched'
                })
            else:
                report_data.append({
                    'annotation_name': bottle,
                    'database_name': bottle,
                    'status': 'direct'
                })
                
        for bottle in bottles_missing_pricing:
            if isinstance(bottle, dict):
                report_data.append({
                    'annotation_name': bottle['annotation_name'],
                    'database_name': bottle['matched_name'],
                    'status': 'missing'
                })
            else:
                report_data.append({
                    'annotation_name': bottle,
                    'database_name': None,
                    'status': 'missing'
                })
                
        # Save report
        report_df = pd.DataFrame(report_data)
        report_df.to_csv(OUTPUT_PATH, index=False)
        print(f"\nFull report saved to: {OUTPUT_PATH}")
    
    print("\n========================================================\n")

if __name__ == "__main__":
    main()
