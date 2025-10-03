import sqlite3
import requests
import json
import time
import os
import re
from pathlib import Path
from tqdm import tqdm


class SuttaTranslator:
    def __init__(self, main_db_path, translation_db_path):
        main_db_path = os.path.expanduser(main_db_path)
        
        if not os.path.exists(main_db_path):
            print(f"❌ Main database not found at: {main_db_path}")
            return
        
        print(f"📁 Main database: {main_db_path}")
        print(f"📁 Translation database: {translation_db_path}")
        
        self.main_db = sqlite3.connect(main_db_path)
        self.translation_db = sqlite3.connect(translation_db_path)
        self.setup_translation_db()
    
    def setup_translation_db(self):
        """Create translation database with updated schema"""
        cursor = self.translation_db.cursor()
        
        # Check if sutta_name column exists
        cursor.execute("PRAGMA table_info(translations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'sutta_name' not in columns:
            print("🔄 Updating translations table schema...")
            # Create new table with updated schema
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sutta_name TEXT,
                original_book_id TEXT,
                original_page_number INTEGER,
                original_paragraph TEXT,
                content_type TEXT,
                original_content TEXT,
                translated_content TEXT,
                language TEXT DEFAULT 'en',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Copy existing data if any
            cursor.execute("""
            INSERT INTO translations_new 
            (original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content, language, created_at)
            SELECT original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content, language, created_at
            FROM translations
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE translations")
            cursor.execute("ALTER TABLE translations_new RENAME TO translations")
            
            self.translation_db.commit()
            print("✅ Translation database schema updated")
        else:
            print("✅ Translation database schema is current")    
    def get_sutta_info(self, sutta_name):
        """Get sutta location info from database"""
        cursor = self.main_db.cursor()
        
        cursor.execute("""
        SELECT book_id, page_number, name 
        FROM suttas 
        WHERE name LIKE ? OR simple LIKE ?
        """, (f'%{sutta_name}%', f'%{sutta_name}%'))
        
        results = cursor.fetchall()
        
        if results:
            print(f"📍 Found sutta '{sutta_name}':")
            for book_id, page_num, name in results:
                print(f"   {book_id} starting at page {page_num}: {name}")
            return results
        else:
            print(f"❌ Sutta '{sutta_name}' not found")
            return []
    
    
    def translate_complete_sutta(self, sutta_name, mula_book_id=None, start_paragraph=None, end_paragraph=None, commentary_book_id=None):
        """Generic function to translate any complete sutta"""
        print(f"🚀 TRANSLATING COMPLETE {sutta_name.upper()}")
        print("=" * 60)
        
        # Auto-detect sutta info if not provided
        if not mula_book_id:
            sutta_info = self.get_sutta_info(sutta_name)
            if not sutta_info:
                return
            mula_book_id, start_page, sutta_name = sutta_info[0]
            start_paragraph, end_paragraph = self.find_sutta_paragraph_range(mula_book_id, start_page)
        
        if not commentary_book_id:
            # Derive commentary book from mula book (mula_di_01 → attha_di_01)
            commentary_book_id = mula_book_id.replace('mula_', 'attha_')
        
        print(f"📖 Mula: {mula_book_id} paragraphs {start_paragraph}-{end_paragraph}")
        print(f"📝 Commentary: {commentary_book_id}")
        
        cursor = self.main_db.cursor()
        
        # Get UNIQUE mula content
        cursor.execute("""
        SELECT DISTINCT pa.content
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = ? 
        AND p.paragraph_number BETWEEN ? AND ?
        ORDER BY p.paragraph_number
        """, (mula_book_id, start_paragraph, end_paragraph))
        
        mula_contents = cursor.fetchall()
        
        # Combine unique mula content
        full_mula_text = ""
        for (content,) in mula_contents:
            clean_content = re.sub(r'<[^>]+>', '', content)
            if sutta_name.lower() not in clean_content.lower() or full_mula_text == "":
                full_mula_text += clean_content + "\n\n"
        
        print(f"📖 {sutta_name} Mula: {len(full_mula_text)} chars")
        
        # Get UNIQUE commentary content
        cursor.execute("""
        SELECT DISTINCT pa.content
        FROM paragraph_mapping pm
        JOIN pages pa ON pa.bookid = pm.exp_book_id AND pa.page = pm.exp_page_number
        WHERE pm.base_book_id = ? 
        AND pm.paragraph BETWEEN ? AND ?
        AND pm.exp_book_id = ?
        ORDER BY pm.exp_page_number
        """, (mula_book_id, start_paragraph, end_paragraph, commentary_book_id))
        
        commentary_contents = cursor.fetchall()
        
        # Combine unique commentary content
        full_commentary_text = ""
        for (content,) in commentary_contents:
            clean_content = re.sub(r'<[^>]+>', '', content)
            full_commentary_text += clean_content + "\n\n"
        
        print(f"📝 {sutta_name} Commentary: {len(full_commentary_text)} chars")
        
        # Smart chunking for mula text
        mula_chunks = self.chunk_text(full_mula_text, max_chars=3500)
        print(f"📦 Mula split into {len(mula_chunks)} chunks")
        
        # Translate mula chunks
        mula_translations = []
        with tqdm(total=len(mula_chunks), desc="Mula chunks") as pbar:
          for i, chunk in enumerate(tqdm(mula_chunks, desc="Translating mula")):
              chunk_id = f"{sutta_name}_mula_{i+1}"
              
              # Check if already translated
              if self.is_chunk_translated(sutta_name, chunk_id, 'mula'):
                  print(f"⏭️  Skipping already translated: {chunk_id}")
                  existing = self.get_existing_translation(sutta_name, chunk_id, 'mula')
                  mula_translations.append(existing)
                  continue
              
              print(f"\n🌐 Translating Mula Chunk {i+1}/{len(mula_chunks)}...")
              translation = self.translate_text(chunk, f"{sutta_name} Mula Part {i+1}")
              
              # Save with chunk-level tracking
              self.save_translation_chunk(
                  sutta_name, mula_book_id, start_paragraph, chunk_id,
                  'mula', chunk, translation
              )
              
              mula_translations.append(translation)
              if i < len(mula_chunks) - 1:
                  time.sleep(3)
              pbar.update(1)
          
        full_mula_translation = "\n\n".join(mula_translations)
        
        time.sleep(5)
        
        # Smart chunking for commentary text
        commentary_chunks = self.chunk_text(full_commentary_text, max_chars=3500)
        print(f"📦 Commentary split into {len(commentary_chunks)} chunks")
        
        # Translate commentary chunks
        commentary_translations = []
        with tqdm(total=len(commentary_chunks), desc="Commentary chunks") as pbar:
          for i, chunk in enumerate(commentary_chunks):
              chunk_id = f"{sutta_name}_commentary_{i+1}"
              
              # Check if already translated
              if self.is_chunk_translated(sutta_name, chunk_id, 'commentary'):
                  print(f"⏭️  Skipping already translated: {chunk_id}")
                  existing = self.get_existing_translation(sutta_name, chunk_id, 'commentary')
                  commentary_translations.append(existing)
                  continue
              
              print(f"\n🌐 Translating Commentary Chunk {i+1}/{len(commentary_chunks)}...")
              translation = self.translate_text(chunk, f"{sutta_name} Commentary Part {i+1}")
              
              # Save with chunk-level tracking
              self.save_translation_chunk(
                  sutta_name, commentary_book_id, start_paragraph, chunk_id,
                  'commentary', chunk, translation
              )
              
              commentary_translations.append(translation)
              if i < len(commentary_chunks) - 1:
                  time.sleep(3)
              pbar.update(1)
          
        full_commentary_translation = "\n\n".join(commentary_translations)
        
        # Generate HTML
        self.generate_sutta_html(
            sutta_name,
            full_mula_text, 
            full_mula_translation,
            full_commentary_text,
            full_commentary_translation
        )
        
        print(f"\n🎉 {sutta_name.upper()} TRANSLATION COMPLETE!")
        print(f"📊 Total chunks: {len(mula_chunks)} mula + {len(commentary_chunks)} commentary")
    
    def chunk_text(self, text, max_chars=3500):
        """Split text into chunks at paragraph boundaries"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += '\n\n' + para
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def find_sutta_paragraph_range(self, book_id, start_page):
        """Find paragraph range for a sutta starting at given page"""
        cursor = self.main_db.cursor()
        
        # Get the actual start paragraph from the start page
        cursor.execute("""
        SELECT MIN(paragraph_number) 
        FROM paragraphs 
        WHERE book_id = ? AND page_number >= ?
        """, (book_id, start_page))
        
        start_para = cursor.fetchone()[0]
        
        # Find the next sutta by looking for sutta markers after our start
        cursor.execute("""
        SELECT p.paragraph_number, p.page_number, substr(pa.content, 1, 200)
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = ? 
        AND p.paragraph_number > ?
        AND (pa.content LIKE '%suttaṃ%' OR pa.content LIKE '%suttavaṇṇanā%')
        AND pa.content NOT LIKE '%brahmajāla%'  
        ORDER BY p.paragraph_number
        LIMIT 1
        """, (book_id, start_para))
        
        next_sutta = cursor.fetchone()
        
        if next_sutta:
            end_para = next_sutta[0] - 1
            print(f"   Found next sutta at paragraph {next_sutta[0]}")
        else:
            # If no next sutta found, go much further
            cursor.execute("""
            SELECT MAX(paragraph_number) 
            FROM paragraphs 
            WHERE book_id = ? AND paragraph_number > ?
            """, (book_id, start_para))
            
            max_para = cursor.fetchone()[0]
            # Use a reasonable range, not just 1 paragraph
            end_para = min(start_para + 200, max_para) if max_para else start_para + 200
            print(f"   Using estimated range to paragraph {end_para}")
        
        print(f"   Paragraph range: {start_para} to {end_para}")
        return start_para, end_para
    
    def translate_text(self, text, context=""):
        """Translate text with streaming progress (clean output)"""
        print(f"🌐 Translating: {context}")
        print(f"   📝 Text length: {len(text)} characters")
        
        payload = {
            'input_sentence': text,
            'input_encoding': 'auto', 
            'target_lang': 'english',
            'do_grammar_explanation': False,
            'model': 'default'
        }
        
        try:
            print("   📤 Sending request...", end="", flush=True)
            response = requests.post(
                "https://dharmamitra.org/next/api/mitra-translation-stream",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=120,
                stream=True
            )
            
            if response.status_code == 200:
                print(" ✅ Request accepted", end="", flush=True)
                
                # ~ full_response = ""
                last_update = 0
                
                # ~ for chunk in response.iter_content(decode_unicode=True, chunk_size=1):
                    # ~ if chunk:
                        # ~ chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                        # ~ full_response += chunk_text
                        
                        # ~ # Update progress every 50 chars (overwrites same line)
                        # ~ if len(full_response) - last_update >= 50:
                            # ~ print(f"\r   📤 Received: {len(full_response)} chars...", end="", flush=True)
                            # ~ last_update = len(full_response)
                
                full_response = ""
                with tqdm(total=len(text), desc="Receiving", unit="char", leave=False) as pbar:
                    for chunk in response.iter_content(decode_unicode=True, chunk_size=100):
                        if chunk:
                            chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                            full_response += chunk_text
                            pbar.update(len(chunk_text))
                translation = full_response.strip()
                print(f"\r   ✅ Translation complete: {len(translation)} characters")
                return translation
                
            else:
                print(f"\n❌ API error: {response.status_code}")
                return f"[TRANSLATION FAILED: {response.status_code}]"
                
        except Exception as e:
            print(f"\n❌ Request failed: {e}")
            return f"[TRANSLATION ERROR: {e}]"
            
    def save_translation_chunk(self, sutta_name, book_id, page_num, chunk_id, content_type, original, translated):
        """Save translation with chunk-level tracking"""
        cursor = self.translation_db.cursor()
        
        cursor.execute("""
        INSERT INTO translations 
        (sutta_name, original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sutta_name, book_id, page_num, chunk_id, content_type, original, translated))
        
        self.translation_db.commit()
        print(f"💾 Saved {content_type} chunk: {chunk_id}")
    
    def is_chunk_translated(self, sutta_name, chunk_id, content_type):
        """Check if chunk is already successfully translated"""
        cursor = self.translation_db.cursor()
        
        cursor.execute("""
        SELECT translated_content FROM translations 
        WHERE sutta_name = ? AND original_paragraph = ? AND content_type = ?
        AND (translated_content NOT LIKE '%[TRANSLATION FAILED%' OR translated_content IS NULL)
        AND (translated_content NOT LIKE '%[TRANSLATION ERROR%' OR translated_content IS NULL) 
        AND (translated_content != '' OR translated_content IS NULL)
        """, (sutta_name, chunk_id, content_type))
        
        result = cursor.fetchone()
        return result is not None and result[0] and len(result[0]) > 0
    
    def get_existing_translation(self, sutta_name, chunk_id, content_type):
        """Get existing translation for a chunk"""
        cursor = self.translation_db.cursor()
        
        cursor.execute("""
        SELECT translated_content FROM translations 
        WHERE sutta_name = ? AND original_paragraph = ? AND content_type = ?
        """, (sutta_name, chunk_id, content_type))
        
        result = cursor.fetchone()
        return result[0] if result else ""
    
    def resume_failed_translations(self, sutta_name=None):
        """Resume translation for failed chunks"""
        print("🔄 RESUMING FAILED TRANSLATIONS")
        print("=" * 50)
        
        cursor = self.translation_db.cursor()
        
        if sutta_name:
            cursor.execute("""
            SELECT sutta_name, original_book_id, original_paragraph, content_type, original_content, translated_content
            FROM translations 
            WHERE sutta_name = ?
            ORDER BY id
            """, (sutta_name,))
        else:
            cursor.execute("""
            SELECT sutta_name, original_book_id, original_paragraph, content_type, original_content, translated_content
            FROM translations 
            ORDER BY id
            """)
        
        all_translations = cursor.fetchall()
        
        failed_translations = []
        for sutta, book_id, paragraph, content_type, original, translated in all_translations:
            if translated and any(error in translated for error in ['[TRANSLATION FAILED', '[TRANSLATION ERROR', 'HTTPSConnectionPool']):
                print(f"❌ Failed: {sutta} - {content_type} - {paragraph}")
                failed_translations.append((sutta, book_id, paragraph, content_type, original))
            elif not translated or translated == '':
                print(f"❌ Empty: {sutta} - {content_type} - {paragraph}")
                failed_translations.append((sutta, book_id, paragraph, content_type, original))
        
        print(f"\n📊 Found {len(failed_translations)} failed translations to retry")
        
        if not failed_translations:
            print("✅ No failed translations found!")
            return
        
        success_count = 0
        for sutta, book_id, paragraph, content_type, original in failed_translations:
            print(f"\n🔄 Retrying: {sutta} - {content_type} - {paragraph}")
            
            # Delete the failed entry
            cursor.execute("""
            DELETE FROM translations 
            WHERE sutta_name = ? AND original_paragraph = ? AND content_type = ?
            """, (sutta, paragraph, content_type))
            
            # Retry translation
            context = f"Retry {sutta} {content_type} {paragraph}"
            new_translation = self.translate_text(original, context)
            
            # Save new translation
            if new_translation and not any(error in new_translation for error in ['[TRANSLATION FAILED', '[TRANSLATION ERROR']):
                cursor.execute("""
                INSERT INTO translations 
                (sutta_name, original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sutta, book_id, 0, paragraph, content_type, original, new_translation))
                
                self.translation_db.commit()
                success_count += 1
                print(f"✅ Retry successful: {content_type} - {paragraph}")
            else:
                print(f"❌ Retry failed again: {content_type} - {paragraph}")
            
            time.sleep(2)
        
        print(f"\n🎉 RESUME COMPLETE: {success_count}/{len(failed_translations)} retries successful")
    
    def generate_sutta_html(self, sutta_name, mula_original, mula_translated, commentary_original, commentary_translated):
        """Generate HTML for any sutta"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{sutta_name} - Complete Translation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ border: 2px solid #333; margin: 30px 0; padding: 20px; border-radius: 10px; }}
                .mula {{ background: #e8f5e8; }}
                .commentary {{ background: #e3f2fd; }}
                .header {{ background: #444; color: white; padding: 15px; border-radius: 5px; }}
                .original {{ color: #666; font-size: 0.9em; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 10px; }}
                .translation {{ color: #000; line-height: 1.5; white-space: pre-wrap; }}
                .note {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <h1>{sutta_name} - Complete Translation</h1>
            
            <div class="note">
                <strong>Note:</strong> Entire sutta and commentary translated as complete texts.<br>
                Manual paragraph matching recommended - commentary references sutta paragraph numbers.
            </div>
            
            <div class="section mula">
                <h2>{sutta_name} (Mula Text)</h2>
                <div class="original">
                    <strong>Original Pali:</strong>
                    <div class="translation">{mula_original}</div>
                </div>
                <div class="translation">
                    <strong>English Translation:</strong>
                    <div class="translation">{mula_translated}</div>
                </div>
            </div>
            
            <div class="section commentary">
                <h2>{sutta_name} Commentary (Aṭṭhakathā)</h2>
                <div class="original">
                    <strong>Original Pali Commentary:</strong>
                    <div class="translation">{commentary_original}</div>
                </div>
                <div class="translation">
                    <strong>English Translation:</strong>
                    <div class="translation">{commentary_translated}</div>
                </div>
            </div>
            
            <div class="note">
                <strong>Usage:</strong> Scroll through both texts. Commentary paragraphs reference sutta paragraph numbers.
            </div>
        </body>
        </html>
        """
        
        filename = f"{sutta_name.lower().replace(' ', '_')}_translation.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated {filename}")
    
    def check_translation_status(self, sutta_name=None):
        """Check status of translations"""
        print("📊 TRANSLATION STATUS CHECK")
        print("=" * 40)
        
        cursor = self.translation_db.cursor()
        
        if sutta_name:
            cursor.execute("""
            SELECT 
                sutta_name,
                content_type,
                COUNT(*) as total,
                SUM(CASE WHEN translated_content LIKE '%[TRANSLATION FAILED%' OR translated_content LIKE '%[TRANSLATION ERROR%' OR translated_content LIKE '%HTTPSConnectionPool%' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN translated_content IS NULL OR translated_content = '' THEN 1 ELSE 0 END) as empty,
                SUM(CASE WHEN translated_content NOT LIKE '%[TRANSLATION%' AND translated_content != '' THEN 1 ELSE 0 END) as success
            FROM translations 
            WHERE sutta_name = ?
            GROUP BY sutta_name, content_type
            """, (sutta_name,))
        else:
            cursor.execute("""
            SELECT 
                sutta_name,
                content_type,
                COUNT(*) as total,
                SUM(CASE WHEN translated_content LIKE '%[TRANSLATION FAILED%' OR translated_content LIKE '%[TRANSLATION ERROR%' OR translated_content LIKE '%HTTPSConnectionPool%' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN translated_content IS NULL OR translated_content = '' THEN 1 ELSE 0 END) as empty,
                SUM(CASE WHEN translated_content NOT LIKE '%[TRANSLATION%' AND translated_content != '' THEN 1 ELSE 0 END) as success
            FROM translations 
            GROUP BY sutta_name, content_type
            """)
        
        results = cursor.fetchall()
        
        for sutta, content_type, total, failed, empty, success in results:
            print(f"\n{sutta} - {content_type.upper()}:")
            print(f"  Total: {total}")
            print(f"  Success: {success}")
            print(f"  Failed: {failed}")
            print(f"  Empty: {empty}")
            if total > 0:
                print(f"  Success Rate: {success/total*100:.1f}%")

# Usage examples
if __name__ == "__main__":
    translator = SuttaTranslator(
        '~/.local/share/com.paauk.tipitaka_pali_reader/tipitaka_pali.db',
        'translations.db'
    )
    
    # Example: Translate DN1 Brahmajāla
    translator.translate_complete_sutta("Brahmajāla")
    
    # Example: Translate with explicit parameters
    # translator.translate_complete_sutta("DN1", "mula_di_01", 1, 149, "attha_di_01")
    
    # Check status and resume if needed
    translator.check_translation_status()
    # translator.resume_failed_translations()
