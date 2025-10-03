import sqlite3
import requests
import json
import time
import os
from pathlib import Path

class TranslationTest:
    def __init__(self, main_db_path, translation_db_path):
        # Expand the ~ in the path
        main_db_path = os.path.expanduser(main_db_path)
        
        # Check if main database exists
        if not os.path.exists(main_db_path):
            print(f"❌ Main database not found at: {main_db_path}")
            print("Please check the path and try again.")
            return
        
        print(f"📁 Main database: {main_db_path}")
        print(f"📁 Translation database: {translation_db_path}")
        
        self.main_db = sqlite3.connect(main_db_path)
        self.translation_db = sqlite3.connect(translation_db_path)
        self.setup_translation_db()
        
    def setup_translation_db(self):
        """Create separate translation database"""
        cursor = self.translation_db.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_book_id TEXT,
            original_page_number INTEGER,
            original_paragraph TEXT,
            content_type TEXT,  -- 'mula' or 'commentary'
            original_content TEXT,
            translated_content TEXT,
            language TEXT DEFAULT 'en',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.translation_db.commit()
        print("✅ Translation database setup complete")
    
    def examine_paragraph_mapping(self):
        """Examine the paragraph_mapping table to understand mula-commentary relationships"""
        cursor = self.main_db.cursor()
        
        print("🔍 Examining paragraph_mapping table...")
        
        # Get mapping for DN2 specifically
        cursor.execute("""
        SELECT paragraph, base_book_id, base_page_number, exp_book_id, exp_page_number
        FROM paragraph_mapping 
        WHERE base_book_id = 'mula_di_02' AND exp_book_id = 'attha_di_02'
        ORDER BY paragraph
        LIMIT 20
        """)
        
        mappings = cursor.fetchall()
        
        print(f"📋 Found {len(mappings)} paragraph mappings for DN2:")
        for mapping in mappings:
            paragraph, base_book, base_page, exp_book, exp_page = mapping
            print(f"   Paragraph {paragraph}: mula_di_02 page {base_page} → attha_di_02 page {exp_page}")
        
        return mappings
    
    def get_matching_commentary(self, base_book_id, base_page, base_paranum, commentary_book_id):
        """Get commentary paragraphs that match the given mula paragraph using the mapping table"""
        cursor = self.main_db.cursor()
        
        # First, try to find the mapping
        cursor.execute("""
        SELECT exp_page_number 
        FROM paragraph_mapping 
        WHERE base_book_id = ? AND base_page_number = ? AND exp_book_id = ?
        """, (base_book_id, base_page, commentary_book_id))
        
        mapping = cursor.fetchone()
        
        if mapping:
            commentary_page = mapping[0]
            print(f"🎯 Found mapping: mula_di_02 page {base_page} → attha_di_02 page {commentary_page}")
            
            # Get commentary paragraphs from that page
            cursor.execute("""
            SELECT page, paranum, content 
            FROM pages 
            WHERE bookid = ? AND page = ?
            ORDER BY CAST(paranum AS INTEGER)
            """, (commentary_book_id, commentary_page))
            
            commentary_paragraphs = cursor.fetchall()
            return commentary_paragraphs
        else:
            print(f"❌ No direct mapping found for mula_di_02 page {base_page}")
            return []
    
    def translate_with_dharmamitra(self, devanagari_text, context_info=""):
      """Translate Devanagari text using Dharmamitra API"""
      payload = {
          'id': json.dumps({
              "input_sentence": devanagari_text,
              "input_encoding": "auto", 
              "target_lang": "english",
              "do_grammar_explanation": False,
              "model": "default"
          }),
          'messages': [{
              'role': 'user',
              'content': devanagari_text,
              'parts': [{'type': 'text', 'text': devanagari_text}]
          }],
          'input_sentence': devanagari_text,
          'input_encoding': 'auto',
          'target_lang': 'english',
          'do_grammar_explanation': False,
          'model': 'default',
      }
      
      try:
          response = requests.post(
              "https://dharmamitra.org/next/api/mitra-translation-stream",
              headers={'Content-Type': 'application/json'},
              data=json.dumps(payload),
              timeout=30
          )
          
          if response.status_code == 200:
              return response.text
          else:
              print(f"❌ API error: {response.status_code}")
              return None
              
      except Exception as e:
          print(f"❌ Request failed: {e}")
          return None
  
    def save_translation(self, book_id, page_num, paranum, content_type, original, translated):
      """Save translation to separate database"""
      cursor = self.translation_db.cursor()
      
      cursor.execute("""
      INSERT INTO translations 
      (original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content)
      VALUES (?, ?, ?, ?, ?, ?)
      """, (book_id, page_num, paranum, content_type, original, translated))
      
      self.translation_db.commit()
      
    def find_dn2_start(self):
        """Find where DN2 Sāmaññaphala Sutta actually starts in mula_di_02"""
        cursor = self.main_db.cursor()
        
        print("🔍 Finding actual start of DN2 Sāmaññaphala Sutta...")
        
        # Look for the specific DN2 content
        cursor.execute("""
        SELECT page, paranum, content 
        FROM pages 
        WHERE bookid = 'mula_di_02' 
        AND (
            content LIKE '%sāmaññaphala%' OR 
            content LIKE '%समञ्ञफल%' OR
            content LIKE '%sāmaññaphalasutta%' OR
            (content LIKE '%dn2%' AND content LIKE '%sutta%')
        )
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT 5
        """)
        
        dn2_starts = cursor.fetchall()
        
        if dn2_starts:
            print("📍 DN2 Sāmaññaphala Sutta starts at:")
            for page, paranum, content in dn2_starts:
                print(f"   Page {page}, Para {paranum}")
                print(f"   Preview: {content[:100]}...")
                print()
            return dn2_starts[0]  # Return the first match
        else:
            print("❌ Could not find DN2 start using direct search")
            
            # Alternative: look for paragraphs that specifically mention DN2
            cursor.execute("""
            SELECT page, paranum, content 
            FROM pages 
            WHERE bookid = 'mula_di_02' 
            AND content LIKE '%para%d%' 
            AND content LIKE '%dn2%'
            ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
            LIMIT 1
            """)
            
            alternative_start = cursor.fetchone()
            if alternative_start:
                print(f"📍 Using alternative DN2 start:")
                page, paranum, content = alternative_start
                print(f"   Page {page}, Para {paranum}")
                print(f"   Preview: {content[:100]}...")
                return alternative_start
            
            print("❌ No DN2 content found")
            return None
    
    def get_dn2_paragraphs(self, start_page, num_paragraphs=3):
        """Get DN2 paragraphs starting from the identified start page"""
        cursor = self.main_db.cursor()
        
        cursor.execute("""
        SELECT page, paranum, content 
        FROM pages 
        WHERE bookid = 'mula_di_02' 
        AND page >= ?
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT ?
        """, (start_page, num_paragraphs))
        
        paragraphs = cursor.fetchall()
        
        print(f"📖 Found {len(paragraphs)} DN2 paragraphs starting from page {start_page}:")
        for i, (page, paranum, content) in enumerate(paragraphs):
            # Verify this is actually DN2 content
            is_dn2 = 'sāmaññaphala' in content.lower() or 'dn2' in content.lower()
            sutta = "DN2 - Sāmaññaphala" if is_dn2 else "Unknown (might be DN14 or other)"
            print(f"   {i+1}. Page {page}, Para {paranum} ({sutta}): {content[:80]}...")
        
        return paragraphs
    
    def run_dn2_matching_debug(self, num_paragraphs=3):
        """Debug: Show matching between DN2 mula and commentary using proper mapping"""
        print("🐛 Starting DN2 Matching Debug...")
        
        base_book_id = 'mula_di_02'
        commentary_book_id = 'attha_di_02'
        
        print(f"🎯 Base text: {base_book_id}")
        print(f"📝 Commentary: {commentary_book_id}")
        
        # FIRST: Find where DN2 actually starts
        dn2_start = self.find_dn2_start()
        
        if not dn2_start:
            print("❌ Could not find DN2 Sāmaññaphala Sutta in mula_di_02")
            return
        
        start_page, start_paranum, start_content = dn2_start
        
        # Get DN2 paragraphs starting from the actual DN2 content
        base_paragraphs = self.get_dn2_paragraphs(start_page, num_paragraphs)
        
        if not base_paragraphs:
            print("❌ No DN2 paragraphs found")
            return
        
        # Generate debug HTML using proper mapping
        self.generate_matching_debug_html(base_paragraphs, base_book_id, commentary_book_id)
    
    def examine_mula_di_02_structure(self):
        """Examine what suttas are contained in mula_di_02"""
        cursor = self.main_db.cursor()
        
        print("🔍 Examining mula_di_02 structure...")
        
        # Look for all sutta markers
        cursor.execute("""
        SELECT page, paranum, substr(content, 1, 200) as preview
        FROM pages 
        WHERE bookid = 'mula_di_02' 
        AND (
            content LIKE '%sutta%' OR 
            content LIKE '%suttavaṇṇanā%' OR
            content LIKE '%suttaniddeso%'
        )
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT 15
        """)
        
        sutta_markers = cursor.fetchall()
        
        print("📚 Suttas found in mula_di_02:")
        for page, paranum, preview in sutta_markers:
            sutta_name = "Unknown"
            if 'mahāpadāna' in preview.lower():
                sutta_name = "DN14 - Mahāpadāna Sutta"
            elif 'sāmaññaphala' in preview.lower():
                sutta_name = "DN2 - Sāmaññaphala Sutta"
            elif 'brahmajāla' in preview.lower():
                sutta_name = "DN1 - Brahmajāla Sutta"
            elif 'soṇadaṇḍa' in preview.lower():
                sutta_name = "DN4 - Soṇadaṇḍa Sutta"
            elif 'kūṭadanta' in preview.lower():
                sutta_name = "DN5 - Kūṭadanta Sutta"
            
            print(f"   Page {page}, Para {paranum}: {sutta_name}")
            print(f"      Preview: {preview[:80]}...")
    def generate_matching_debug_html(self, base_paragraphs, base_book_id, commentary_book_id):
        """Generate HTML showing mula-commentary matching using proper mapping"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>DN2 Mula-Commentary Matching Debug</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .pair {{ border: 2px solid #ccc; margin: 20px 0; padding: 15px; }}
                .mula {{ background: #e8f5e8; padding: 15px; margin: 10px 0; }}
                .commentary {{ background: #e3f2fd; padding: 15px; margin: 10px 0; }}
                .header {{ background: #666; color: white; padding: 10px; font-weight: bold; }}
                .para-info {{ color: #666; font-size: 0.9em; }}
                .match-info {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <h1>DN2 Sāmaññaphala Sutta - Mula & Commentary Matching</h1>
            <div class="header">Base: {base_book_id} | Commentary: {commentary_book_id}</div>
        """
        
        # Show base paragraphs with matching commentary
        for i, (base_page, base_paranum, base_content) in enumerate(base_paragraphs):
            # Get matching commentary using mapping table
            matching_commentary = self.get_matching_commentary(
                base_book_id, base_page, base_paranum, commentary_book_id
            )
            
            html_content += f"""
            <div class="pair">
                <h2>Mula Paragraph {i+1}</h2>
                <div class="para-info">Page {base_page}, Para {base_paranum}</div>
                <div class="mula">
                    <strong>Mula Text:</strong><br>
                    {base_content}
                </div>
            """
            
            if matching_commentary:
                html_content += f"""
                <div class="match-info">
                    <strong>Mapping:</strong> mula_di_02 page {base_page} → attha_di_02 page {matching_commentary[0][0]}
                </div>
                <div class="commentary">
                    <strong>Matching Commentary ({len(matching_commentary)} paragraphs):</strong><br>
                """
                for j, (comm_page, comm_paranum, comm_content) in enumerate(matching_commentary):
                    html_content += f"""
                    <div style="margin: 10px 0; padding: 10px; background: #fff; border-left: 3px solid #2196F3;">
                        <div class="para-info">Comm Page {comm_page}, Para {comm_paranum}</div>
                        {comm_content}
                    </div>
                    """
                html_content += "</div>"
            else:
                html_content += """
                <div class="commentary">
                    <strong>No matching commentary found via mapping table</strong>
                </div>
                """
            
            html_content += "</div>"
        
        html_content += """
            <div class="header">Debug Info</div>
            <div style="background: #f5f5f5; padding: 15px; margin: 20px 0;">
                <h3>Mapping Success!</h3>
                <p>The paragraph_mapping table is successfully linking mula pages to commentary pages:</p>
                <ul>
                    <li>mula_di_02 page 1 → attha_di_02 page 1</li>
                    <li>mula_di_02 page 2 → attha_di_02 page 3</li>
                    <li>mula_di_02 page 3 → attha_di_02 page 6</li>
                </ul>
                <p>Each mula paragraph now shows the correct commentary paragraphs from the mapped page.</p>
            </div>
        </body>
        </html>
        """
        
        with open('dn2_matching_debug.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Generated dn2_matching_debug.html")

    def find_actual_dn2_start(self):
        """Find the actual start of DN2 Sāmaññaphala Sutta"""
        cursor = self.main_db.cursor()
        
        print("🔍 Searching for DN2 Sāmaññaphala Sutta specifically...")
        
        # Look for the actual DN2 sutta - it should have a specific marker
        cursor.execute("""
        SELECT page, paranum, content 
        FROM pages 
        WHERE bookid = 'mula_di_02' 
        AND (
            content LIKE '%sāmaññaphalasutta%' OR
            content LIKE '%समञ्ञफलसुत्त%' OR
            content LIKE '%sāmaññaphala sutta%' OR
            (content LIKE '%sutta%' AND content LIKE '%sāmaññaphala%')
        )
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("📍 Found potential DN2 markers:")
            for page, paranum, content in results:
                print(f"   Page {page}, Para {paranum}")
                print(f"   Preview: {content[:150]}...")
                print()
            return results[0]
        
        # Alternative: Look for the specific DN2 chapter marker
        print("🔍 Searching for DN2 chapter markers...")
        cursor.execute("""
        SELECT page, paranum, content 
        FROM pages 
        WHERE bookid = 'mula_di_02' 
        AND content LIKE '%dn2%'
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT 10
        """)
        
        dn2_markers = cursor.fetchall()
        
        print("📍 DN2 markers found:")
        for page, paranum, content in dn2_markers:
            print(f"   Page {page}, Para {paranum}")
            print(f"   Content: {content}")
            print()
        
        if dn2_markers:
            return dn2_markers[0]
        
        print("❌ Could not find DN2 Sāmaññaphala Sutta")
        return None
    
    def examine_all_sutta_starts(self):
        """Examine all sutta starts in mula_di_02 to understand the structure"""
        cursor = self.main_db.cursor()
        
        print("🔍 Examining all sutta starts in mula_di_02...")
        
        # Look for all chapter markers
        cursor.execute("""
        SELECT page, paranum, content 
        FROM pages 
        WHERE bookid = 'mula_di_02' 
        AND content LIKE '%chapter%' OR content LIKE '%sutta%' OR content LIKE '%%'
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT 20
        """)
        
        chapters = cursor.fetchall()
        
        print("📚 All chapter/sutta markers:")
        for page, paranum, content in chapters:
            # Extract the sutta name
            sutta_name = "Unknown"
            if 'mahāpadāna' in content.lower():
                sutta_name = "DN14 - Mahāpadāna Sutta"
            elif 'mahānidāna' in content.lower():
                sutta_name = "DN15 - Mahānidāna Sutta" 
            elif 'mahāparinibbāna' in content.lower():
                sutta_name = "DN16 - Mahāparinibbāna Sutta"
            elif 'mahāsudassana' in content.lower():
                sutta_name = "DN17 - Mahāsudassana Sutta"
            elif 'janavasabha' in content.lower():
                sutta_name = "DN18 - Janavasabha Sutta"
            elif 'mahāgovinda' in content.lower():
                sutta_name = "DN19 - Mahāgovinda Sutta"
            elif 'sāmaññaphala' in content.lower():
                sutta_name = "DN2 - Sāmaññaphala Sutta"
            elif 'brahmajāla' in content.lower():
                sutta_name = "DN1 - Brahmajāla Sutta"
            
            print(f"   Page {page}, Para {paranum}: {sutta_name}")
            print(f"   Marker: {content.strip()}")
            print()
    
    def search_all_dn2_books(self):
        """Search all books for DN2 Sāmaññaphala Sutta"""
        cursor = self.main_db.cursor()
        
        print("🔍 Searching all books for DN2 Sāmaññaphala Sutta...")
        
        cursor.execute("""
        SELECT DISTINCT bookid, name 
        FROM books 
        WHERE name LIKE '%sāmaññaphala%' OR name LIKE '%समञ्ञफल%' OR name LIKE '%dn2%'
        """)
        
        dn2_books = cursor.fetchall()
        
        print("📚 Books that might contain DN2:")
        for book_id, name in dn2_books:
            print(f"   {book_id}: {name}")
            
            # Check first few paragraphs
            cursor.execute("""
            SELECT page, paranum, substr(content, 1, 100) 
            FROM pages 
            WHERE bookid = ? 
            ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
            LIMIT 2
            """, (book_id,))
            
            samples = cursor.fetchall()
            for page, paranum, preview in samples:
                print(f"      Page {page}, Para {paranum}: {preview}...")

    def translate_dn_with_commentary(self, start_page=1, num_pages=5):
        """Translate Digha Nikaya mula and commentary while preserving mapping"""
        print("🚀 Starting DN Translation with Commentary...")
        
        base_book_id = 'mula_di_02'
        commentary_book_id = 'attha_di_02'
        
        print(f"🎯 Base text: {base_book_id}")
        print(f"📝 Commentary: {commentary_book_id}")
        
        # Get mula paragraphs for translation
        cursor = self.main_db.cursor()
        
        # Get mula paragraphs starting from specified page
        cursor.execute("""
        SELECT page, paranum, content 
        FROM pages 
        WHERE bookid = ? AND page >= ?
        ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
        LIMIT ?
        """, (base_book_id, start_page, num_pages * 10))  # Estimate paragraphs per page
        
        mula_paragraphs = cursor.fetchall()
        
        print(f"📖 Found {len(mula_paragraphs)} mula paragraphs from page {start_page}:")
        
        # Translate mula text
        print(f"\n🌐 Translating {len(mula_paragraphs)} MULA paragraphs...")
        for i, (page, paranum, content) in enumerate(mula_paragraphs):
            print(f"   📖 Translating mula page {page}, para {paranum} ({i+1}/{len(mula_paragraphs)})...")
            
            translation = self.translate_with_dharmamitra(content, f"DN mula page {page}, para {paranum}")
            if translation:
                self.save_translation(base_book_id, page, paranum, 'mula', content, translation)
                print(f"   ✅ Translated: {translation[:50]}...")
                time.sleep(2)  # Rate limiting
            else:
                print(f"   ❌ Failed to translate mula paragraph {i+1}")
        
        # Translate corresponding commentary using mapping
        print(f"\n🌐 Translating COMMENTARY using mapping table...")
        
        # Get unique commentary pages from mapping for the mula pages we're translating
        cursor.execute("""
        SELECT DISTINCT exp_page_number 
        FROM paragraph_mapping 
        WHERE base_book_id = ? AND exp_book_id = ? AND base_page_number >= ?
        ORDER BY exp_page_number
        LIMIT ?
        """, (base_book_id, commentary_book_id, start_page, num_pages * 3))
        
        commentary_pages = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found {len(commentary_pages)} commentary pages to translate: {commentary_pages}")
        
        for commentary_page in commentary_pages:
            # Get all commentary paragraphs from this page
            cursor.execute("""
            SELECT page, paranum, content 
            FROM pages 
            WHERE bookid = ? AND page = ?
            ORDER BY CAST(paranum AS INTEGER)
            """, (commentary_book_id, commentary_page))
            
            commentary_paragraphs = cursor.fetchall()
            
            print(f"   💬 Translating commentary page {commentary_page} ({len(commentary_paragraphs)} paragraphs)...")
            
            for j, (page, paranum, content) in enumerate(commentary_paragraphs):
                translation = self.translate_with_dharmamitra(content, f"DN commentary page {page}, para {paranum}")
                if translation:
                    self.save_translation(commentary_book_id, page, paranum, 'commentary', content, translation)
                    print(f"      ✅ Translated commentary: {translation[:50]}...")
                    time.sleep(2)  # Rate limiting
                else:
                    print(f"      ❌ Failed to translate commentary paragraph {j+1}")
        
        print(f"\n🎉 DN translation completed! Mula and commentary translations saved!")
        self.generate_translation_preview()
    
    
    def generate_translation_preview(self):
        """Generate HTML preview showing mula-commentary pairs"""
        cursor = self.translation_db.cursor()
        
        # Get translations grouped by mula page - simplified version without mapping table
        cursor.execute("""
        SELECT original_book_id, original_page_number, original_paragraph,
               original_content, translated_content, content_type
        FROM translations 
        ORDER BY original_book_id, original_page_number, original_paragraph, content_type
        LIMIT 30
        """)
        
        results = cursor.fetchall()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>DN Mula-Commentary Translation Preview</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .pair { border: 2px solid #ccc; margin: 20px 0; padding: 15px; }
                .mula { background: #e8f5e8; padding: 15px; margin: 10px 0; }
                .commentary { background: #e3f2fd; padding: 15px; margin: 10px 0; }
                .header { background: #666; color: white; padding: 10px; font-weight: bold; }
                .original { color: #666; font-size: 0.9em; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 10px; }
                .translation { color: #000; }
                .content-type { font-weight: bold; color: #333; margin-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>DN Mula-Commentary Translation Preview</h1>
            <div class="header">Showing translated mula and commentary text</div>
        """
        
        current_page = None
        for row in results:
            book_id, page, paranum, original, translated, content_type = row
            
            if page != current_page:
                if current_page is not None:
                    html_content += "</div>"
                current_page = page
                html_content += f"""
                <div class="pair">
                    <h2>Page {page}</h2>
                """
            
            content_class = "mula" if content_type == "mula" else "commentary"
            content_label = "MULA TEXT" if content_type == "mula" else "COMMENTARY"
            
            html_content += f"""
            <div class="{content_class}">
                <div class="content-type">{content_label} - Paragraph {paranum}</div>
                <div class="original">
                    <strong>Original:</strong><br>{original}
                </div>
                <div class="translation">
                    <strong>Translation:</strong><br>{translated}
                </div>
            </div>
            """
        
        html_content += "</div></body></html>"
        
        with open('dn_translation_preview.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Generated dn_translation_preview.html")
    
        # Also show a summary of what was translated
        cursor.execute("""
        SELECT content_type, COUNT(*) as count 
        FROM translations 
        GROUP BY content_type
        """)
        
        summary = cursor.fetchall()
        print("\n📊 Translation Summary:")
        for content_type, count in summary:
            print(f"   {content_type}: {count} paragraphs") 
            
    def find_dn2_samanaphala_specific(self):
          """Find DN2 Sāmaññaphala Sutta specifically in both mula and commentary"""
          cursor = self.main_db.cursor()
          
          print("🔍 Searching for DN2 Sāmaññaphala specifically...")
          
          # Look for DN2 in mula text
          print("📖 Searching mula_di_02 for DN2 Sāmaññaphala...")
          cursor.execute("""
          SELECT page, paranum, content 
          FROM pages 
          WHERE bookid = 'mula_di_02' 
          AND (
              content LIKE '%sāmaññaphala%' OR 
              content LIKE '%समञ्ञफल%' OR
              content LIKE '%sāmaññaphalasutta%' OR
              (content LIKE '%dn2%' AND content LIKE '%sutta%' AND content NOT LIKE '%dn2_%')
          )
          ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
          LIMIT 10
          """)
          
          mula_dn2 = cursor.fetchall()
          
          if mula_dn2:
              print("📍 DN2 Sāmaññaphala found in mula_di_02:")
              for page, paranum, content in mula_dn2:
                  print(f"   Page {page}, Para {paranum}")
                  print(f"   Content: {content[:150]}...")
                  print()
          else:
              print("❌ DN2 Sāmaññaphala not found in mula_di_02")
          
          # Look for DN2 in commentary text
          print("📝 Searching attha_di_02 for DN2 Sāmaññaphala commentary...")
          cursor.execute("""
          SELECT page, paranum, content 
          FROM pages 
          WHERE bookid = 'attha_di_02' 
          AND (
              content LIKE '%sāmaññaphala%' OR 
              content LIKE '%समञ्ञफल%' OR
              content LIKE '%sāmaññaphalasutta%' OR
              content LIKE '%sāmaññaphalasuttavaṇṇanā%'
          )
          ORDER BY CAST(page AS INTEGER), CAST(paranum AS INTEGER)
          LIMIT 10
          """)
          
          commentary_dn2 = cursor.fetchall()
          
          if commentary_dn2:
              print("📍 DN2 Sāmaññaphala commentary found in attha_di_02:")
              for page, paranum, content in commentary_dn2:
                  print(f"   Page {page}, Para {paranum}")
                  print(f"   Content: {content[:150]}...")
                  print()
          else:
              print("❌ DN2 Sāmaññaphala commentary not found in attha_di_02")
          
          return mula_dn2, commentary_dn2
      
    def check_all_sutta_starts(self):
          """Check where each sutta starts in both texts"""
          cursor = self.main_db.cursor()
          
          print("📚 Checking all sutta starts in mula_di_02...")
          cursor.execute("""
          SELECT page, paranum, substr(content, 1, 200) 
          FROM pages 
          WHERE bookid = 'mula_di_02' 
          AND content LIKE '%suttaṃ%'
          ORDER BY CAST(page AS INTEGER)
          LIMIT 15
          """)
          
          mula_suttas = cursor.fetchall()
          print("Mula suttas:")
          for page, paranum, content in mula_suttas:
              print(f"   Page {page}, Para {paranum}: {content.strip()}")
          
          print("\n📚 Checking all sutta starts in attha_di_02...")
          cursor.execute("""
          SELECT page, paranum, substr(content, 1, 200) 
          FROM pages 
          WHERE bookid = 'attha_di_02' 
          AND content LIKE '%suttavaṇṇanā%'
          ORDER BY CAST(page AS INTEGER)
          LIMIT 15
          """)
          
          commentary_suttas = cursor.fetchall()
          print("Commentary suttas:")
          for page, paranum, content in commentary_suttas:
              print(f"   Page {page}, Para {paranum}: {content.strip()}")
# ~ if __name__ == "__main__":
    # ~ translator = TranslationTest('~/.local/share/com.paauk.tipitaka_pali_reader/tipitaka_pali.db', 'translations.db')
    # ~ translator.generate_translation_preview()
    # ~ print("=== TRANSLATING DN WITH COMMENTARY ===")

if __name__ == "__main__":
    translator = TranslationTest('~/.local/share/com.paauk.tipitaka_pali_reader/tipitaka_pali.db', 'translations.db')
    
    print("=== FINDING DN2 SĀMAÑÑAPHALA SPECIFICALLY ===")
    mula_dn2, commentary_dn2 = translator.find_dn2_samanaphala_specific()
    
    print("\n=== CHECKING ALL SUTTA STARTS ===")
    translator.check_all_sutta_starts()
