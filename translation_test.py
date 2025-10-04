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
    
    
    # ~ def translate_complete_sutta(self, sutta_name, mula_book_id=None, start_paragraph=None, end_paragraph=None, commentary_book_id=None):
        # ~ """Generic function to translate any complete sutta"""
        # ~ print(f"🚀 TRANSLATING COMPLETE {sutta_name.upper()}")
        # ~ print("=" * 60)
        
        # ~ # Auto-detect sutta info if not provided
        # ~ if not mula_book_id:
            # ~ sutta_info = self.get_sutta_info(sutta_name)
            # ~ if not sutta_info:
                # ~ return
            # ~ mula_book_id, start_page, sutta_name = sutta_info[0]
            # ~ start_paragraph, end_paragraph = self.find_sutta_paragraph_range(mula_book_id, start_page)
        
        # ~ if not commentary_book_id:
            # ~ # Derive commentary book from mula book (mula_di_01 → attha_di_01)
            # ~ commentary_book_id = mula_book_id.replace('mula_', 'attha_')
        
        # ~ print(f"📖 Mula: {mula_book_id} paragraphs {start_paragraph}-{end_paragraph}")
        # ~ print(f"📝 Commentary: {commentary_book_id}")
        
        # ~ cursor = self.main_db.cursor()
        
        # ~ # Get UNIQUE mula content
        # ~ cursor.execute("""
        # ~ SELECT DISTINCT pa.content
        # ~ FROM paragraphs p
        # ~ JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        # ~ WHERE p.book_id = ? 
        # ~ AND p.paragraph_number BETWEEN ? AND ?
        # ~ ORDER BY p.paragraph_number
        # ~ """, (mula_book_id, start_paragraph, end_paragraph))
        
        # ~ mula_contents = cursor.fetchall()
        
        # ~ # Combine unique mula content
        # ~ full_mula_text = ""
        # ~ for (content,) in mula_contents:
            # ~ clean_content = re.sub(r'<[^>]+>', '', content)
            # ~ if sutta_name.lower() not in clean_content.lower() or full_mula_text == "":
                # ~ full_mula_text += clean_content + "\n\n"
        
        # ~ print(f"📖 {sutta_name} Mula: {len(full_mula_text)} chars")
        
        # ~ # Get UNIQUE commentary content
        # ~ cursor.execute("""
        # ~ SELECT DISTINCT pa.content
        # ~ FROM paragraph_mapping pm
        # ~ JOIN pages pa ON pa.bookid = pm.exp_book_id AND pa.page = pm.exp_page_number
        # ~ WHERE pm.base_book_id = ? 
        # ~ AND pm.paragraph BETWEEN ? AND ?
        # ~ AND pm.exp_book_id = ?
        # ~ ORDER BY pm.exp_page_number
        # ~ """, (mula_book_id, start_paragraph, end_paragraph, commentary_book_id))
        
        # ~ commentary_contents = cursor.fetchall()
        
        # ~ # Combine unique commentary content
        # ~ full_commentary_text = ""
        # ~ for (content,) in commentary_contents:
            # ~ clean_content = re.sub(r'<[^>]+>', '', content)
            # ~ full_commentary_text += clean_content + "\n\n"
        
        # ~ print(f"📝 {sutta_name} Commentary: {len(full_commentary_text)} chars")
        
        # ~ # Smart chunking for mula text
        # ~ mula_chunks = self.chunk_text(full_mula_text, max_chars=3500)
        # ~ print(f"📦 Mula split into {len(mula_chunks)} chunks")
        
        # ~ # Translate mula chunks
        # ~ mula_translations = []
        # ~ with tqdm(total=len(mula_chunks), desc="Mula chunks") as pbar:
          # ~ for i, chunk in enumerate(tqdm(mula_chunks, desc="Translating mula")):
              # ~ chunk_id = f"{sutta_name}_mula_{i+1}"
              
              # ~ # Check if already translated
              # ~ if self.is_chunk_translated(sutta_name, chunk_id, 'mula'):
                  # ~ print(f"⏭️  Skipping already translated: {chunk_id}")
                  # ~ existing = self.get_existing_translation(sutta_name, chunk_id, 'mula')
                  # ~ mula_translations.append(existing)
                  # ~ continue
              
              # ~ print(f"\n🌐 Translating Mula Chunk {i+1}/{len(mula_chunks)}...")
              # ~ translation = self.translate_text(chunk, f"{sutta_name} Mula Part {i+1}")
              
              # ~ # Save with chunk-level tracking
              # ~ self.save_translation_chunk(
                  # ~ sutta_name, mula_book_id, start_paragraph, chunk_id,
                  # ~ 'mula', chunk, translation
              # ~ )
              
              # ~ mula_translations.append(translation)
              # ~ if i < len(mula_chunks) - 1:
                  # ~ time.sleep(3)
              # ~ pbar.update(1)
          
        # ~ full_mula_translation = "\n\n".join(mula_translations)
        
        # ~ time.sleep(5)
        
        # ~ # Smart chunking for commentary text
        # ~ commentary_chunks = self.chunk_text(full_commentary_text, max_chars=3500)
        # ~ print(f"📦 Commentary split into {len(commentary_chunks)} chunks")
        
        # ~ # Translate commentary chunks
        # ~ commentary_translations = []
        # ~ with tqdm(total=len(commentary_chunks), desc="Commentary chunks") as pbar:
          # ~ for i, chunk in enumerate(commentary_chunks):
              # ~ chunk_id = f"{sutta_name}_commentary_{i+1}"
              
              # ~ # Check if already translated
              # ~ if self.is_chunk_translated(sutta_name, chunk_id, 'commentary'):
                  # ~ print(f"⏭️  Skipping already translated: {chunk_id}")
                  # ~ existing = self.get_existing_translation(sutta_name, chunk_id, 'commentary')
                  # ~ commentary_translations.append(existing)
                  # ~ continue
              
              # ~ print(f"\n🌐 Translating Commentary Chunk {i+1}/{len(commentary_chunks)}...")
              # ~ translation = self.translate_text(chunk, f"{sutta_name} Commentary Part {i+1}")
              
              # ~ # Save with chunk-level tracking
              # ~ self.save_translation_chunk(
                  # ~ sutta_name, commentary_book_id, start_paragraph, chunk_id,
                  # ~ 'commentary', chunk, translation
              # ~ )
              
              # ~ commentary_translations.append(translation)
              # ~ if i < len(commentary_chunks) - 1:
                  # ~ time.sleep(3)
              # ~ pbar.update(1)
          
        # ~ full_commentary_translation = "\n\n".join(commentary_translations)
        
        # ~ # Generate HTML
        # ~ self.generate_sutta_html(
            # ~ sutta_name,
            # ~ full_mula_text, 
            # ~ full_mula_translation,
            # ~ full_commentary_text,
            # ~ full_commentary_translation
        # ~ )
        
        # ~ print(f"\n🎉 {sutta_name.upper()} TRANSLATION COMPLETE!")
        # ~ print(f"📊 Total chunks: {len(mula_chunks)} mula + {len(commentary_chunks)} commentary")
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
          
          # Translate mula chunks with clean progress
          mula_translations = []
          with tqdm(total=len(mula_chunks), desc="📚 Mula Translation", position=0) as main_bar:
              with tqdm(total=1, desc="Current chunk", position=1, leave=False) as chunk_bar:
                  for i, chunk in enumerate(mula_chunks):
                      chunk_id = f"{sutta_name}_mula_{i+1}"
                      
                      # Update progress descriptions
                      main_bar.set_description(f"📚 Mula {i+1}/{len(mula_chunks)}")
                      chunk_bar.set_description(f"📝 {len(chunk)} chars")
                      
                      # Check if already translated
                      if self.is_chunk_translated(sutta_name, chunk_id, 'mula'):
                          existing = self.get_existing_translation(sutta_name, chunk_id, 'mula')
                          mula_translations.append(existing)
                          chunk_bar.set_description("⏭️ Skipped (already done)")
                          chunk_bar.reset()
                          main_bar.update(1)
                          continue
                      
                      # Translate
                      translation = self.translate_text(chunk, f"{sutta_name} Mula Part {i+1}")
                      
                      # Save with chunk-level tracking
                      self.save_translation_chunk(
                          sutta_name, mula_book_id, start_paragraph, chunk_id,
                          'mula', chunk, translation
                      )
                      
                      mula_translations.append(translation)
                      chunk_bar.set_description(f"✅ {len(translation)} chars")
                      chunk_bar.reset()
                      
                      if i < len(mula_chunks) - 1:
                          time.sleep(3)
                      main_bar.update(1)
          
          full_mula_translation = "\n\n".join(mula_translations)
          
          time.sleep(5)
          
          # Smart chunking for commentary text
          commentary_chunks = self.chunk_text(full_commentary_text, max_chars=3500)
          print(f"📦 Commentary split into {len(commentary_chunks)} chunks")
          
          # Translate commentary chunks with clean progress
          commentary_translations = []
          with tqdm(total=len(commentary_chunks), desc="📝 Commentary Translation", position=0) as main_bar:
              with tqdm(total=1, desc="Current chunk", position=1, leave=False) as chunk_bar:
                  for i, chunk in enumerate(commentary_chunks):
                      chunk_id = f"{sutta_name}_commentary_{i+1}"
                      
                      # Update progress descriptions
                      main_bar.set_description(f"📝 Commentary {i+1}/{len(commentary_chunks)}")
                      chunk_bar.set_description(f"📝 {len(chunk)} chars")
                      
                      # Check if already translated
                      if self.is_chunk_translated(sutta_name, chunk_id, 'commentary'):
                          existing = self.get_existing_translation(sutta_name, chunk_id, 'commentary')
                          commentary_translations.append(existing)
                          chunk_bar.set_description("⏭️ Skipped (already done)")
                          chunk_bar.reset()
                          main_bar.update(1)
                          continue
                      
                      # Translate
                      translation = self.translate_text(chunk, f"{sutta_name} Commentary Part {i+1}")
                      
                      # Save with chunk-level tracking
                      self.save_translation_chunk(
                          sutta_name, commentary_book_id, start_paragraph, chunk_id,
                          'commentary', chunk, translation
                      )
                      
                      commentary_translations.append(translation)
                      chunk_bar.set_description(f"✅ {len(translation)} chars")
                      chunk_bar.reset()
                      
                      if i < len(commentary_chunks) - 1:
                          time.sleep(3)
                      main_bar.update(1)
          
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
    def translate_entire_book(self, mula_book_id, commentary_book_id):
        """Translate all suttas in a mula book"""
        cursor = self.main_db.cursor()
        
        # Get all suttas in this book
        cursor.execute("""
        SELECT name, page_number 
        FROM suttas 
        WHERE book_id = ?
        ORDER BY page_number
        """, (mula_book_id,))
        
        suttas = cursor.fetchall()
        
        for sutta_name, start_page in suttas:
            print(f"\n🎯 Processing {sutta_name}...")
            self.translate_complete_sutta(sutta_name, mula_book_id, start_page, None, commentary_book_id)
    
    def translate_entire_digha(self):
        """Translate all 34 Dīgha Nikāya suttas"""
        print("🚀 TRANSLATING ENTIRE DĪGHA NIKĀYA")
        
        # DN1-13
        self.translate_entire_book("mula_di_01", "attha_di_01")
        # DN14-23  
        self.translate_entire_book("mula_di_02", "attha_di_02")
        # DN24-34
        self.translate_entire_book("mula_di_03", "attha_di_03")        
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
    
    def translate_sutta_by_number(self, dn_number):
        """Translate sutta by DN number (e.g., DN3, DN15)"""
        cursor = self.main_db.cursor()
        
        # Map DN numbers to book ranges
        dn_ranges = {
            (1, 13): ("mula_di_01", "attha_di_01"),
            (14, 23): ("mula_di_02", "attha_di_02"), 
            (24, 34): ("mula_di_03", "attha_di_03")
        }
        
        # Find which book this DN number belongs to
        mula_book = None
        commentary_book = None
        for (start, end), (mula, commentary) in dn_ranges.items():
            if start <= dn_number <= end:
                mula_book, commentary_book = mula, commentary
                break
        
        if not mula_book:
            print(f"❌ DN{dn_number} not found in valid range (1-34)")
            return
        
        # Get sutta info for this DN number
        cursor.execute("""
        SELECT name, page_number 
        FROM suttas 
        WHERE book_id = ?
        ORDER BY page_number
        LIMIT 1 OFFSET ?
        """, (mula_book, dn_number - (1 if dn_number <= 13 else 14 if dn_number <= 23 else 24)))
        
        sutta_info = cursor.fetchone()
        
        if sutta_info:
            sutta_name, start_page = sutta_info
            print(f"🎯 Translating DN{dn_number}: {sutta_name}")
            self.translate_complete_sutta(sutta_name, mula_book, start_page, None, commentary_book)
        else:
            print(f"❌ DN{dn_number} not found in database")
    
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

    def debug_sutta_range(self, sutta_name):
        """Debug paragraph range for a sutta"""
        cursor = self.main_db.cursor()
        
        # Find the sutta
        cursor.execute("""
        SELECT book_id, page_number FROM suttas 
        WHERE name LIKE ? LIMIT 1
        """, (f'%{sutta_name}%',))
        
        sutta_info = cursor.fetchone()
        if not sutta_info:
            print(f"❌ Sutta '{sutta_name}' not found")
            return
            
        book_id, start_page = sutta_info
        print(f"📍 {sutta_name}: {book_id} starting at page {start_page}")
        
        # Check what paragraphs exist at this page
        cursor.execute("""
        SELECT p.paragraph_number, p.page_number, substr(pa.content, 1, 100)
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = ? AND p.page_number >= ?
        ORDER BY p.paragraph_number
        LIMIT 10
        """, (book_id, start_page))
        
        paragraphs = cursor.fetchall()
        print(f"📖 First 10 paragraphs at page {start_page}:")
        for para_num, page_num, content in paragraphs:
            print(f"   Para {para_num} (Page {page_num}): {content}...")
            
    def check_paragraph_sequence(self, book_id):
        """Check paragraph numbers to find sutta boundaries"""
        cursor = self.main_db.cursor()
        
        cursor.execute("""
        SELECT p.paragraph_number, p.page_number, substr(pa.content, 1, 150)
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = ?
        AND p.paragraph_number BETWEEN 190 AND 250
        ORDER BY p.paragraph_number
        """, (book_id,))
        
        paragraphs = cursor.fetchall()
        
        print(f"📖 Paragraphs in {book_id} after DN2:")
        for para_num, page_num, content in paragraphs:
            # Look for sutta markers
            sutta_marker = ""
            if 'suttaṃ' in content.lower():
                sutta_marker = " 🚨 SUTTA"
            print(f"   Para {para_num} (Page {page_num}): {content[:80]}...{sutta_marker}")
  
    def map_sutta_ranges(self, mula_book_id):
        """Find exact paragraph ranges for all suttas in a book"""
        cursor = self.main_db.cursor()
        
        # Get all suttas in this book with their start pages
        cursor.execute("""
        SELECT name, page_number 
        FROM suttas 
        WHERE book_id = ?
        ORDER BY page_number
        """, (mula_book_id,))
        
        suttas = cursor.fetchall()
        
        ranges = []
        for i, (sutta_name, start_page) in enumerate(suttas):
            # Find start paragraph for this sutta
            cursor.execute("""
            SELECT MIN(paragraph_number)
            FROM paragraphs 
            WHERE book_id = ? AND page_number >= ?
            """, (mula_book_id, start_page))
            
            start_para = cursor.fetchone()[0]
            
            # Find end paragraph (start of next sutta or end of book)
            if i < len(suttas) - 1:
                next_start_page = suttas[i+1][1]
                cursor.execute("""
                SELECT MIN(paragraph_number) - 1
                FROM paragraphs 
                WHERE book_id = ? AND page_number >= ?
                """, (mula_book_id, next_start_page))
                end_para = cursor.fetchone()[0]
            else:
                # Last sutta in book - go to max paragraph
                cursor.execute("""
                SELECT MAX(paragraph_number)
                FROM paragraphs 
                WHERE book_id = ?
                """, (mula_book_id,))
                end_para = cursor.fetchone()[0]
            
            ranges.append((sutta_name, start_para, end_para))
            print(f"📖 {sutta_name}: paragraphs {start_para}-{end_para}")
        
        return ranges
    
    def translate_book_by_ranges(self, mula_book_id, commentary_book_id):
        """Translate entire book using auto-mapped paragraph ranges"""
        print(f"🗺️  Mapping sutta ranges for {mula_book_id}...")
        ranges = self.map_sutta_ranges(mula_book_id)
        
        print(f"🚀 Translating {len(ranges)} suttas in {mula_book_id}...")
        for sutta_name, start_para, end_para in ranges:
            self.translate_complete_sutta(sutta_name, mula_book_id, start_para, end_para, commentary_book_id)
            
    def debug_none_chunks(self):
        """Check chunks with None sutta_name"""
        cursor = self.translation_db.cursor()
        
        cursor.execute("""
        SELECT original_book_id, original_paragraph, content_type, original_content, translated_content
        FROM translations 
        WHERE sutta_name IS NULL OR sutta_name = 'None'
        """)
        
        none_chunks = cursor.fetchall()
        
        print(f"🔍 Found {len(none_chunks)} chunks with None sutta_name:")
        for book_id, paragraph, content_type, original, translated in none_chunks:
            print(f"   {book_id} - {content_type} - {paragraph}")
            print(f"   Original: {original[:100]}...")
            print(f"   Translated: {translated[:100]}...")
            print()
    def clean_none_chunks(self):
        """Clean up chunks with None sutta_name that are causing false failures"""
        cursor = self.translation_db.cursor()
        
        # Delete all chunks with None sutta_name
        cursor.execute("""
        DELETE FROM translations 
        WHERE sutta_name IS NULL OR sutta_name = 'None'
        """)
        
        deleted_count = cursor.rowcount
        self.translation_db.commit()
        
        print(f"🧹 Cleaned {deleted_count} chunks with None sutta_name")
        print("✅ These were mostly header content and duplicates from early testing")
        
        # Now run resume to fix actual failed chunks
        print("\n🔄 Now resuming actual failed translations...")
        self.resume_failed_translations()
        
        
    def generate_sutta_html_from_db(self, sutta_name):
        """Generate HTML for a sutta by loading from database"""
        cursor = self.translation_db.cursor()
        
        # Get all mula chunks for this sutta
        cursor.execute("""
        SELECT original_content, translated_content 
        FROM translations 
        WHERE sutta_name = ? AND content_type = 'mula'
        ORDER BY original_paragraph
        """, (sutta_name,))
        
        mula_chunks = cursor.fetchall()
        
        # Combine mula content
        full_mula_original = ""
        full_mula_translated = ""
        for orig, trans in mula_chunks:
            full_mula_original += orig + "\n\n"
            full_mula_translated += trans + "\n\n"
        
        # Get all commentary chunks for this sutta
        cursor.execute("""
        SELECT original_content, translated_content 
        FROM translations 
        WHERE sutta_name = ? AND content_type = 'commentary'
        ORDER BY original_paragraph
        """, (sutta_name,))
        
        commentary_chunks = cursor.fetchall()
        
        # Combine commentary content
        full_commentary_original = ""
        full_commentary_translated = ""
        for orig, trans in commentary_chunks:
            full_commentary_original += orig + "\n\n"
            full_commentary_translated += trans + "\n\n"
        
        # Generate HTML
        self.generate_sutta_html(
            sutta_name,
            full_mula_original,
            full_mula_translated, 
            full_commentary_original,
            full_commentary_translated
        )      

    def translate_entire_book_complete(self, mula_book_id, commentary_book_id):
        """Translate ALL paragraphs in a book, regardless of sutta boundaries"""
        cursor = self.main_db.cursor()
        
        # Get ALL paragraphs in the book
        cursor.execute("""
        SELECT MIN(paragraph_number), MAX(paragraph_number)
        FROM paragraphs 
        WHERE book_id = ?
        """, (mula_book_id,))
        
        start_para, end_para = cursor.fetchone()
        
        print(f"📚 Translating ENTIRE {mula_book_id}: paragraphs {start_para}-{end_para}")
        
        # Use a generic sutta name for the whole book
        sutta_name = f"complete_{mula_book_id}"
        
        # Translate all paragraphs as one big text
        self.translate_complete_sutta(sutta_name, mula_book_id, start_para, end_para, commentary_book_id)

    def get_accurate_sutta_ranges(self, mula_book_id):
        """Get accurate sutta ranges from the suttas table"""
        cursor = self.main_db.cursor()
        
        # Get all suttas in this book with their start pages
        cursor.execute("""
        SELECT name, page_number 
        FROM suttas 
        WHERE book_id = ?
        ORDER BY page_number
        """, (mula_book_id,))
        
        suttas = cursor.fetchall()
        ranges = []
        
        for i, (sutta_name, start_page) in enumerate(suttas):
            # Find start paragraph from start page
            cursor.execute("""
            SELECT MIN(paragraph_number)
            FROM paragraphs 
            WHERE book_id = ? AND page_number >= ?
            """, (mula_book_id, start_page))
            start_para = cursor.fetchone()[0]
            
            # End paragraph is start of next sutta minus 1, or end of book
            if i < len(suttas) - 1:
                next_start_page = suttas[i+1][1]
                cursor.execute("""
                SELECT MIN(paragraph_number) - 1
                FROM paragraphs 
                WHERE book_id = ? AND page_number >= ?
                """, (mula_book_id, next_start_page))
                end_para = cursor.fetchone()[0]
            else:
                # Last sutta - go to max paragraph
                cursor.execute("""
                SELECT MAX(paragraph_number)
                FROM paragraphs 
                WHERE book_id = ?
                """, (mula_book_id,))
                end_para = cursor.fetchone()[0]
            
            ranges.append((sutta_name, start_para, end_para))
            print(f"📖 {sutta_name}: paragraphs {start_para}-{end_para}")
        
        return ranges
        
    def generate_individual_sutta_htmls(self, mula_book_id):
        """Generate separate HTML files for each sutta using paragraph ranges"""
        # Get the mapped sutta ranges we found earlier
        ranges = self.map_sutta_ranges(mula_book_id)
        
        for sutta_name, start_para, end_para in ranges:
            print(f"🎨 Generating HTML for {sutta_name} (paragraphs {start_para}-{end_para})")
            self.generate_sutta_html_from_db(sutta_name)
    
    
    def generate_sutta_html(self, sutta_name, pali_mula, trans_mula, pali_commentary, trans_commentary):
        """Generate interactive HTML with toggleable commentary for serious Pali study"""
        
        # Parse paragraphs with numbers
        mula_paragraphs = self.parse_numbered_paragraphs(pali_mula, trans_mula)
        commentary_paragraphs = self.parse_numbered_paragraphs(pali_commentary, trans_commentary)
        
        # Create paragraph number mapping for commentary
        commentary_map = {}
        for para in commentary_paragraphs:
            commentary_map[para['number']] = para
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{sutta_name} - Pali Study</title>
            <style>
                body {{
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background: #f8f9fa;
                    color: #333;
                }}
                
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 20px;
                }}
                
                .sutta-title {{
                    font-size: 2em;
                    color: #2c5530;
                    margin: 0;
                    font-weight: 300;
                }}
                
                .controls {{
                    display: flex;
                    gap: 15px;
                    margin: 20px 0;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    flex-wrap: wrap;
                }}
                
                .control-btn {{
                    padding: 8px 16px;
                    border: 1px solid #6c757d;
                    background: white;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                
                .control-btn:hover {{
                    background: #495057;
                    color: white;
                }}
                
                .control-btn.active {{
                    background: #2c5530;
                    color: white;
                    border-color: #2c5530;
                }}
                
                .paragraph {{
                    margin-bottom: 25px;
                    border-left: 3px solid transparent;
                    padding-left: 15px;
                    transition: border-color 0.3s ease;
                }}
                
                .paragraph:hover {{
                    border-left-color: #2c5530;
                }}
                
                .para-number {{
                    font-weight: bold;
                    color: #2c5530;
                    margin-right: 10px;
                    min-width: 40px;
                    display: inline-block;
                }}
                
                .pali-text {{
                    font-family: "Noto Sans", Arial, sans-serif;
                    font-size: 1.1em;
                    color: #1a1a1a;
                    margin-bottom: 8px;
                }}
                
                .translation {{
                    color: #666;
                    font-style: italic;
                    margin-bottom: 15px;
                    padding-left: 40px;
                }}
                
                .commentary {{
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0 10px 40px;
                    display: none;
                }}
                
                .commentary.show {{
                    display: block;
                    animation: fadeIn 0.3s ease;
                }}
                
                .commentary-header {{
                    font-weight: bold;
                    color: #6c757d;
                    margin-bottom: 8px;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .commentary-pali {{
                    font-family: "Noto Sans", Arial, sans-serif;
                    color: #495057;
                    margin-bottom: 5px;
                }}
                
                .commentary-trans {{
                    color: #6c757d;
                    font-style: italic;
                    padding-left: 20px;
                }}
                
                .pali-only .translation,
                .pali-only .commentary-trans {{
                    display: none;
                }}
                
                .trans-only .pali-text,
                .trans-only .commentary-pali {{
                    display: none;
                }}
                
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(-10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 15px;
                    }}
                    
                    .controls {{
                        flex-direction: column;
                    }}
                    
                    .translation {{
                        padding-left: 20px;
                    }}
                    
                    .commentary {{
                        margin-left: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="sutta-title">{sutta_name}</h1>
                </div>
                
                <div class="controls">
                    <button class="control-btn" onclick="toggleCommentary()">
                        <span id="commentary-btn">🔍 Show Commentary</span>
                    </button>
                    <button class="control-btn active" onclick="setViewMode('both')">Both Texts</button>
                    <button class="control-btn" onclick="setViewMode('pali')">Pali Only</button>
                    <button class="control-btn" onclick="setViewMode('trans')">Translation Only</button>
                </div>
                
                <div class="content" id="sutta-content">
        """
        
        # Generate paragraphs with optional commentary
        for para in mula_paragraphs:
            para_num = para['number']
            has_commentary = para_num in commentary_map
            
            html_content += f"""
                    <div class="paragraph" data-para="{para_num}">
                        <div class="pali-text">
                            <span class="para-number">{para_num}.</span>
                            {para['pali']}
                        </div>
                        <div class="translation">
                            {para['translation']}
                        </div>
            """
            
            if has_commentary:
                comm = commentary_map[para_num]
                html_content += f"""
                        <div class="commentary" id="commentary-{para_num}">
                            <div class="commentary-header">Commentary</div>
                            <div class="commentary-pali">
                                <span class="para-number">{para_num}.</span>
                                {comm['pali']}
                            </div>
                            <div class="commentary-trans">
                                {comm['translation']}
                            </div>
                        </div>
                """
            
            html_content += "</div>"
        
        html_content += """
                </div>
            </div>
            
            <script>
                let commentaryVisible = false;
                let currentViewMode = 'both';
                
                function toggleCommentary() {{
                    commentaryVisible = !commentaryVisible;
                    const commentaries = document.querySelectorAll('.commentary');
                    const btn = document.getElementById('commentary-btn');
                    
                    commentaries.forEach(comm => {{
                        if (commentaryVisible) {{
                            comm.classList.add('show');
                        }} else {{
                            comm.classList.remove('show');
                        }}
                    }});
                    
                    btn.textContent = commentaryVisible ? '🔍 Hide Commentary' : '🔍 Show Commentary';
                }}
                
                function setViewMode(mode) {{
                    currentViewMode = mode;
                    document.body.className = mode + '-only';
                    
                    // Update button states
                    document.querySelectorAll('.control-btn').forEach(btn => {{
                        btn.classList.remove('active');
                    }});
                    event.target.classList.add('active');
                }}
                
                // Keyboard shortcuts
                document.addEventListener('keydown', (e) => {{
                    if (e.key === 'c' || e.key === 'C') {{
                        toggleCommentary();
                    }} else if (e.key === '1') {{
                        setViewMode('both');
                    }} else if (e.key === '2') {{
                        setViewMode('pali');
                    }} else if (e.key === '3') {{
                        setViewMode('trans');
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Save HTML file
        filename = f"{sutta_name.replace(' ', '_').lower()}_study.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 Generated study HTML: {filename}")
        return filename
    
    def parse_numbered_paragraphs(self, pali_text, trans_text):
        """Parse numbered paragraphs from text"""
        paragraphs = []
        
        # Split by paragraph numbers (like "288. ", "289. ", etc.)
        pali_paras = re.split(r'(\d+\.)\s+', pali_text)
        trans_paras = re.split(r'(\d+\.)\s+', trans_text)
        
        # Process in pairs (number, content)
        for i in range(1, len(pali_paras), 2):
            if i + 1 < len(pali_paras):
                para_num = pali_paras[i].strip('.')
                pali_content = pali_paras[i + 1].strip()
                
                # Find corresponding translation
                trans_content = self.find_translation_for_paragraph(trans_paras, para_num)
                
                paragraphs.append({
                    'number': para_num,
                    'pali': pali_content,
                    'translation': trans_content
                })
        
        return paragraphs
    
    def find_translation_for_paragraph(self, trans_paras, para_num):
        """Find translation for a specific paragraph number"""
        for i in range(1, len(trans_paras), 2):
            if i + 1 < len(trans_paras) and trans_paras[i].strip('.') == para_num:
                return trans_paras[i + 1].strip()
        return "Translation not available"
        
    def get_mula_text_from_db(self, book_id, start_para, end_para):
        """Get original Pali mula text from main database"""
        cursor = self.main_db.cursor()
        cursor.execute("""
            SELECT p.paragraph_number, pa.content
            FROM paragraphs p
            JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
            WHERE p.book_id = ? AND p.paragraph_number BETWEEN ? AND ?
            ORDER BY p.paragraph_number
        """, (book_id, start_para, end_para))
        
        paragraphs = []
        for para_num, content in cursor.fetchall():
            clean_content = re.sub(r'<[^>]+>', '', content)
            paragraphs.append(f"{para_num}. {clean_content}")
        
        return "\n".join(paragraphs)

    def get_mula_translation_from_db(self, book_id, start_para, end_para):
        """Get mula translation from translations database"""
        cursor = self.main_db.cursor()
        cursor.execute("""
            SELECT chunk_id, translation 
            FROM translations 
            WHERE book_id = ? AND chunk_type = 'mula'
            ORDER BY chunk_id
        """, (book_id,))
        
        # Reconstruct full translation by combining chunks
        full_translation = ""
        for chunk_id, translation in cursor.fetchall():
            full_translation += translation + "\n\n"
        
        return full_translation
    def generate_html_for_sutta(self, sutta_name, mula_book_id, start_para, end_para):
        """Generate HTML for a complete sutta using database translations"""
        
        # 1. Extract mula Pali and translation from database
        mula_pali = self.get_mula_text_from_db(mula_book_id, start_para, end_para)
        mula_trans = self.get_mula_translation_from_db(mula_book_id, start_para, end_para)
        
        # 2. Extract commentary Pali and translation  
        commentary_book_id = mula_book_id.replace('mula_', 'attha_')
        commentary_pali = self.get_commentary_text_from_db(commentary_book_id, start_para, end_para)
        commentary_trans = self.get_commentary_translation_from_db(commentary_book_id, start_para, end_para)
        
        # 3. Generate HTML
        return self.generate_sutta_html(
            sutta_name,
            mula_pali,
            mula_trans,
            commentary_pali, 
            commentary_trans
        )
    def generate_all_sutta_html(self, book_id):
        """Generate HTML for all suttas in a book"""
        
        # Sutta boundaries for DN1-13 in mula_di_01
        sutta_boundaries = {
            "DN1 Brahmajala Sutta": (1, 150),
            "DN2 Samannaphala Sutta": (151, 350), 
            "DN3 Ambattha Sutta": (351, 500),
            # ... add all DN1-13 boundaries
        }
        
        for sutta_name, (start_para, end_para) in sutta_boundaries.items():
            print(f"📄 Generating HTML for {sutta_name}...")
            self.generate_html_for_sutta(sutta_name, book_id, start_para, end_para)
          
  
    def generate_html_from_translations(self, sutta_name):
        """Generate HTML for a sutta using existing chunk translations"""
        
        # 1. Get all mula chunks for this sutta from translation_chunks table in trans_db
        cursor = self.main_db.cursor()
        cursor.execute("""
            SELECT chunk_id, original_text, translation 
            FROM translations
            WHERE sutta_name = ? AND chunk_type = 'mula'
            ORDER BY chunk_id
        """, (sutta_name,))
        
        mula_chunks = cursor.fetchall()
        
        # 2. Get all commentary chunks for this sutta
        cursor.execute("""
            SELECT chunk_id, original_text, translation 
            FROM translations 
            WHERE sutta_name = ? AND chunk_type = 'commentary' 
            ORDER BY chunk_id
        """, (sutta_name,))
        
        commentary_chunks = cursor.fetchall()
        
        # 3. Combine chunks into full texts
        full_mula_pali = "\n\n".join([chunk[1] for chunk in mula_chunks])
        full_mula_trans = "\n\n".join([chunk[2] for chunk in mula_chunks])
        full_comm_pali = "\n\n".join([chunk[1] for chunk in commentary_chunks])
        full_comm_trans = "\n\n".join([chunk[2] for chunk in commentary_chunks])
        
        # 4. Generate HTML
        return self.generate_sutta_html(
            sutta_name,
            full_mula_pali,
            full_mula_trans,
            full_comm_pali,
            full_comm_trans
        )
  
if __name__ == "__main__":
    translator = SuttaTranslator(
        '~/.local/share/com.paauk.tipitaka_pali_reader/tipitaka_pali.db',
        'translations.db'
    )
    
    # Example: Translate DN1 Brahmajāla
    # ~ translator.translate_complete_sutta("Brahmajāla")
    
    # ~ # Example: Translate with explicit parameters
    # ~ # translator.translate_complete_sutta("DN1", "mula_di_01", 1, 149, "attha_di_01")
    
    # ~ # Check status and resume if needed
    # ~ translator.check_translation_status()
    # ~ # translator.resume_failed_translations()
    
    # ~ # Translate ALL Dīgha suttas automatically
    # ~ translator.translate_entire_digha()
    
    # ~ # Or just one book
    # ~ translator.translate_entire_book("mula_di_01", "attha_di_01")
    
    
    # Translate by DN number
    # ~ translator.translate_sutta_by_number(3)   # DN3 Ambatṭha
    # ~ translator.translate_sutta_by_number(15)  # DN15 Mahānidāna
    # ~ translator.translate_sutta_by_number(1)   # DN1 Brahmajāla (will skip)
    # ~ translator.debug_sutta_range("ambatṭha")
    # ~ translator.check_paragraph_sequence("mula_di_01")
    # ~ translator.translate_book_by_ranges("mula_di_01", "attha_di_01")
    # ~ translator.check_translation_status()
    # ~ translator.resume_failed_translations()
    # ~ translator.clean_none_chunks()
    # ~ translator.generate_sutta_html_from_db("ambaṭṭhasuttaṃ")
    # ~ translator.generate_sutta_html_from_db("kevaṭṭasuttaṃ") 
    # ~ translator.generate_sutta_html_from_db("kūṭadantasuttaṃ")
    
    # Also regenerate any others that might need updating
    # ~ translator.generate_sutta_html_from_db("jāliyasuttaṃ") 
    # This will translate EVERY paragraph in mula_di_01, no cutting off
    # ~ translator.translate_entire_book_complete("mula_di_01", "attha_di_01")
    # After your batch translation completes

    
    # ~ translator.generate_all_sutta_html("mula_di_01")
    translator.generate_html_from_translations("Brahmajala Sutta")
   
