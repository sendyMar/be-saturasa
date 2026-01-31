import sqlite3
import json

def dump_themes_sqlite():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Django default table name for core.Template app
        cursor.execute("SELECT id_theme, name, category, path FROM core_template")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append({
                "id_theme": row[0],
                "name": row[1],
                "category": row[2],
                "path": row[3]
            })
        
        print(json.dumps(data, indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    dump_themes_sqlite()
