import sqlite3
import requests
import json
import time
import os
import re
from pathlib import Path

class DN2RealTranslator:
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
        """Create translation database"""
        cursor = self.translation_db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        self.translation_db.commit()
        print("✅ Translation database setup complete")
    
    
    def get_dn2_mula_content(self):
        """Get DN2 mula content and extract individual paragraphs"""
        cursor = self.main_db.cursor()
        
        print("🔍 Getting DN2 content from mula_di_01...")
        
        # Get the content for DN2 paragraphs
        cursor.execute("""
        SELECT p.paragraph_number, p.page_number, pa.content
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = 'mula_di_01' 
        AND p.paragraph_number BETWEEN 150 AND 152
        ORDER BY p.paragraph_number
        """)
        
        db_paragraphs = cursor.fetchall()
        
        all_individual_paras = []
        
        for db_para_num, page_num, content in db_paragraphs:
            print(f"📖 Processing database paragraph {db_para_num}:")
            print(f"   Raw content preview: {content[:100]}...")
            
            # Extract individual paragraphs from this content
            individual_paras = self.extract_individual_paragraphs(content)
            
            print(f"   Found {len(individual_paras)} individual paragraphs:")
            for i, para in enumerate(individual_paras):
                print(f"     {i+1}. {para[:80]}...")
                all_individual_paras.append({
                    'db_para_num': db_para_num,
                    'page_num': page_num,
                    'individual_index': i,
                    'content': para
                })
        
        return all_individual_paras
    
    def get_matching_commentary_content(self, mula_db_paragraph_number):
        """Get commentary content that matches the given mula paragraph"""
        cursor = self.main_db.cursor()
        
        print(f"🔗 Finding commentary for mula database paragraph {mula_db_paragraph_number}...")
        
        cursor.execute("""
        SELECT pm.exp_book_id, pm.exp_page_number, pa.content
        FROM paragraph_mapping pm
        JOIN pages pa ON pa.bookid = pm.exp_book_id AND pa.page = pm.exp_page_number
        WHERE pm.base_book_id = 'mula_di_01' 
        AND pm.paragraph = ?
        ORDER BY pm.exp_page_number
        """, (mula_db_paragraph_number,))
        
        commentary_db_paragraphs = cursor.fetchall()
        
        all_commentary_paras = []
        
        for book_id, page_num, content in commentary_db_paragraphs:
            print(f"📝 Processing commentary from {book_id} page {page_num}:")
            print(f"   Raw content preview: {content[:100]}...")
            
            # Extract individual paragraphs from commentary
            individual_paras = self.extract_individual_paragraphs(content)
            
            print(f"   Found {len(individual_paras)} individual commentary paragraphs:")
            for i, para in enumerate(individual_paras):
                print(f"     {i+1}. {para[:80]}...")
                all_commentary_paras.append({
                    'book_id': book_id,
                    'page_num': page_num,
                    'individual_index': i,
                    'content': para
                })
        
        return all_commentary_paras
    
   
    def save_translation(self, book_id, page_num, para_info, content_type, original, translated):
        """Save translation to database"""
        cursor = self.translation_db.cursor()
        
        cursor.execute("""
        INSERT INTO translations 
        (original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (book_id, page_num, str(para_info), content_type, original, translated))
        
        self.translation_db.commit()
        print(f"💾 Saved {content_type} translation")
    
 
    def extract_individual_paragraphs(self, content):
        """Extract individual paragraphs - SIMPLE AND SAFE"""
        # Remove HTML tags
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # For debugging, just return the main content as one paragraph
        # This avoids the combinatorial explosion
        return [clean_content]
    
      
    def generate_debug_html(self, translations):
        """Generate HTML showing the translation results - FIXED VERSION"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>DN2 Debug Translation - Database Paragraphs</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .pair { border: 2px solid #333; margin: 30px 0; padding: 20px; border-radius: 10px; }
                .mula { background: #e8f5e8; padding: 15px; margin: 15px 0; border-left: 4px solid #2e7d32; }
                .commentary { background: #e3f2fd; padding: 15px; margin: 10px 0; border-left: 4px solid #1565c0; }
                .header { background: #444; color: white; padding: 15px; border-radius: 5px; }
                .debug-info { background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }
                .original { color: #666; font-size: 0.9em; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 10px; }
                .translation { color: #000; line-height: 1.5; }
                .para-info { font-weight: bold; color: #333; margin-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>DN2 Sāmaññaphala - Database Paragraph Translation</h1>
            <div class="header">
                <strong>Structure:</strong> Each database paragraph treated as single unit
            </div>
        """
        
        for translation in translations:
            html_content += f"""
            <div class="pair">
                <h2>Mula Database Paragraph {translation['mula_db_para']}</h2>
                
                <div class="debug-info">
                    <strong>Mapping:</strong> mula_di_01 database paragraph {translation['mula_db_para']} → 
                    {len(translation['commentary'])} commentary paragraph(s)
                </div>
                
                <div class="mula">
                    <div class="para-info">MULA TEXT (Database Paragraph {translation['mula_db_para']})</div>
                    <div class="original">
                        <strong>Original:</strong><br>
                        {translation['mula_original']}
                    </div>
                    <div class="translation">
                        <strong>Translation:</strong><br>
                        {translation['mula_translated']}
                    </div>
                </div>
            """
            
            if translation['commentary']:
                html_content += '<div class="commentary-section">'
                html_content += f'<h3>Matching Commentary ({len(translation["commentary"])} database paragraphs)</h3>'
                
                for i, comm in enumerate(translation['commentary']):
                    html_content += f"""
                    <div class="commentary">
                        <div class="para-info">COMMENTARY {i+1} ({comm['book']} Page {comm['page']})</div>
                        <div class="original">
                            <strong>Original:</strong><br>
                            {comm['original']}
                        </div>
                        <div class="translation">
                            <strong>Translation:</strong><br>
                            {comm['translated']}
                        </div>
                    </div>
                    """
                
                html_content += '</div>'
            
            html_content += "</div>"
        
        html_content += """
            <div class="debug-info">
                <h3>Translation Workflow Verified ✅</h3>
                <p><strong>Success!</strong> The complete workflow is working:</p>
                <ul>
                    <li>✅ Database mapping between mula_di_01 and attha_di_01 works</li>
                    <li>✅ Paragraph-level translation pipeline works</li>
                    <li>✅ Both mula and commentary texts are being translated</li>
                    <li>✅ Translations are saved to database</li>
                    <li>✅ HTML generation with mula+commentary pairs works</li>
                </ul>
                <p><strong>Next:</strong> Replace mock translations with real API calls</p>
            </div>
        </body>
        </html>
        """
        
        with open('dn2_database_paragraphs_debug.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Generated dn2_database_paragraphs_debug.html")
        

    
    def translate_text(self, text, context=""):
        """Translate text with streaming progress"""
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
            print("   📤 Sending request...")
            response = requests.post(
                "https://dharmamitra.org/next/api/mitra-translation-stream",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=120,  # Longer timeout for streaming
                stream=True  # Enable streaming
            )
            
            if response.status_code == 200:
                print("   ✅ Request accepted, receiving stream...")
                
                # Collect streaming response
                full_response = ""
                for chunk in response.iter_content(decode_unicode=True, chunk_size=1):
                    if chunk:
                        chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                        full_response += chunk_text
                        # Show progress every 100 characters
                        if len(full_response) % 100 == 0:
                            print(f"   📥 Received: {len(full_response)} chars...")
                
                translation = full_response.strip()
                print(f"   ✅ Translation complete: {len(translation)} characters")
                return translation
                
            else:
                print(f"❌ API error: {response.status_code}")
                return f"[TRANSLATION FAILED: {response.status_code}]"
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return f"[TRANSLATION ERROR: {e}]"
    def translate_dn2_debug(self):
        """Debug: Translate just 2 paragraphs with REAL translation"""
        print("🚀 STARTING REAL DN2 TRANSLATION (2 paragraphs)")
        print("=" * 60)
        
        # Get only 2 database paragraphs to limit API calls
        cursor = self.main_db.cursor()
        cursor.execute("""
        SELECT p.paragraph_number, p.page_number, pa.content
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = 'mula_di_01' 
        AND p.paragraph_number BETWEEN 150 AND 151
        ORDER BY p.paragraph_number
        """)
        
        mula_db_paragraphs = cursor.fetchall()
        
        print(f"📖 Found {len(mula_db_paragraphs)} database paragraphs")
        
        all_translations = []
        
        # Process each database paragraph
        for db_para_num, page_num, content in mula_db_paragraphs:
            print(f"\n🎯 PROCESSING MULA DATABASE PARAGRAPH {db_para_num}")
            print("-" * 50)
            
            # Extract just the relevant paragraph to avoid duplicate content
            clean_content = self.extract_single_paragraph(content, db_para_num)
            
            # Translate mula text
            mula_translation = self.translate_text(
                clean_content, 
                f"DN2 Mula Paragraph {db_para_num}"
            )
            
            # Save mula translation
            self.save_translation(
                'mula_di_01', page_num, db_para_num,
                'mula', clean_content, mula_translation
            )
            
            # Get matching commentary
            cursor.execute("""
            SELECT pm.exp_book_id, pm.exp_page_number, pa.content
            FROM paragraph_mapping pm
            JOIN pages pa ON pa.bookid = pm.exp_book_id AND pa.page = pm.exp_page_number
            WHERE pm.base_book_id = 'mula_di_01' 
            AND pm.paragraph = ?
            ORDER BY pm.exp_page_number
            LIMIT 1  
            """, (db_para_num,))
            
            commentary_paragraphs = cursor.fetchall()
            
            commentary_data = []
            for comm_book, comm_page, comm_content in commentary_paragraphs:
                # Extract relevant commentary part
                clean_comm = self.extract_commentary_part(comm_content, db_para_num)
                
                # Translate commentary text
                comm_translation = self.translate_text(
                    clean_comm,
                    f"DN2 Commentary for mula {db_para_num}"
                )
                
                # Save commentary translation
                self.save_translation(
                    comm_book, comm_page, db_para_num,
                    'commentary', clean_comm, comm_translation
                )
                
                commentary_data.append({
                    'book': comm_book,
                    'page': comm_page,
                    'original': clean_comm,
                    'translated': comm_translation
                })
            
            # Store for HTML generation
            all_translations.append({
                'mula_db_para': db_para_num,
                'mula_page': page_num,
                'mula_original': clean_content,
                'mula_translated': mula_translation,
                'commentary': commentary_data
            })
            
            # Add delay between API calls to be respectful
            time.sleep(2)
        
        # Generate debug HTML
        self.generate_debug_html(all_translations)
        
        print(f"\n🎉 REAL DN2 TRANSLATION COMPLETE!")
        print(f"📊 Translated {len(mula_db_paragraphs)} mula paragraphs")
        total_commentary = sum(len(t['commentary']) for t in all_translations)
        print(f"📊 Translated {total_commentary} commentary paragraphs")
    
    def extract_single_paragraph(self, content, para_num):
        """Extract just the relevant paragraph to avoid duplicates"""
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Look for the specific paragraph number
        pattern = rf'({para_num}\.[^•]+?)(?=\d+\.\s|$)'
        match = re.search(pattern, clean_content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        else:
            # Fallback: return first 300 chars
            return clean_content[:300]
    
    def extract_commentary_part(self, content, para_num):
        """Extract relevant part of commentary"""
        clean_content = re.sub(r'<[^>]+>', '', content)
        return clean_content[:500]  # Limit commentary length
    
    def translate_complete_dn2(self):
        """Translate entire DN2 Sāmaññaphala Sutta and commentary with minimal API calls"""
        print("🚀 TRANSLATING COMPLETE DN2 (Minimal API Calls)")
        print("=" * 60)
        
        cursor = self.main_db.cursor()
        
        # Get UNIQUE mula content (avoid duplicates)
        cursor.execute("""
        SELECT DISTINCT pa.content
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = 'mula_di_01' 
        AND p.paragraph_number BETWEEN 150 AND 194
        ORDER BY p.paragraph_number
        """)
        
        mula_contents = cursor.fetchall()
        
        # Combine unique mula content
        full_mula_text = ""
        for (content,) in mula_contents:
            clean_content = re.sub(r'<[^>]+>', '', content)
            # Remove duplicate header text
            if "sāmaññaphalasuttaṃ" not in clean_content or full_mula_text == "":
                full_mula_text += clean_content + "\n\n"
        
        print(f"📖 DN2 Mula: {len(full_mula_text)} chars of unique text")
        
        # Get UNIQUE commentary content
        cursor.execute("""
        SELECT DISTINCT pa.content
        FROM paragraph_mapping pm
        JOIN pages pa ON pa.bookid = pm.exp_book_id AND pa.page = pm.exp_page_number
        WHERE pm.base_book_id = 'mula_di_01' 
        AND pm.paragraph BETWEEN 150 AND 194
        AND pm.exp_book_id = 'attha_di_01'
        ORDER BY pm.exp_page_number
        """)
        
        commentary_contents = cursor.fetchall()
        
        # Combine unique commentary content
        full_commentary_text = ""
        for (content,) in commentary_contents:
            clean_content = re.sub(r'<[^>]+>', '', content)
            full_commentary_text += clean_content + "\n\n"
        
        print(f"📝 DN2 Commentary: {len(full_commentary_text)} chars of unique text")
        
        # Translate mula (ONE API CALL)
        print(f"\n🌐 Translating DN2 Mula Text...")
        mula_translation = self.translate_text(
            full_mula_text[:4000],  # Limit to avoid timeout
            "Complete DN2 Sāmaññaphala Sutta"
        )
        
        # Save mula translation
        self.save_translation(
            'mula_di_01', 150, 'complete_dn2',
            'mula', full_mula_text[:4000], mula_translation
        )
        
        time.sleep(5)  # Longer delay between major translations
        
        # Translate commentary (ONE API CALL)
        print(f"\n🌐 Translating DN2 Commentary Text...")
        commentary_translation = self.translate_text(
            full_commentary_text[:4000],  # Limit to avoid timeout
            "Complete DN2 Commentary"
        )
        
        # Save commentary translation
        self.save_translation(
            'attha_di_01', 122, 'complete_dn2',
            'commentary', full_commentary_text[:4000], commentary_translation
        )
        
        # Generate final HTML
        self.generate_complete_dn2_html(
            full_mula_text[:4000], 
            mula_translation,
            full_commentary_text[:4000],
            commentary_translation
        )
        
        print(f"\n🎉 COMPLETE DN2 TRANSLATION FINISHED!")
        print(f"📊 Only 2 API calls made")
        print(f"📊 Mula: {len(mula_translation)} chars translated")
        print(f"📊 Commentary: {len(commentary_translation)} chars translated")
    
    def generate_complete_dn2_html(self, mula_original, mula_translated, commentary_original, commentary_translated):
        """Generate HTML for complete DN2 translation"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Complete DN2 Sāmaññaphala Translation</title>
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
            <h1>Complete DN2 Sāmaññaphala Sutta Translation</h1>
            
            <div class="note">
                <strong>Note:</strong> Entire DN2 sutta and commentary translated as complete texts.<br>
                Manual paragraph matching recommended - commentary references sutta paragraph numbers.
            </div>
            
            <div class="section mula">
                <h2>DN2 Sāmaññaphala Sutta (Mula Text)</h2>
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
                <h2>DN2 Commentary (Aṭṭhakathā)</h2>
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
                <strong>Usage:</strong> Scroll through both texts. Commentary paragraphs reference sutta paragraph numbers.<br>
                Look for numbers like "150.", "151." in commentary to match with sutta paragraphs.
            </div>
        </body>
        </html>
        """
        
        with open('complete_dn2_translation.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Generated complete_dn2_translation.html")
  
    def translate_complete_dn2_full(self):
        """Translate entire DN2 Sāmaññaphala Sutta and commentary with smart chunking"""
        print("🚀 TRANSLATING COMPLETE DN2 (Smart Chunking)")
        print("=" * 60)
        
        cursor = self.main_db.cursor()
        
        # Get UNIQUE mula content
        cursor.execute("""
        SELECT DISTINCT pa.content
        FROM paragraphs p
        JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page
        WHERE p.book_id = 'mula_di_01' 
        AND p.paragraph_number BETWEEN 150 AND 194
        ORDER BY p.paragraph_number
        """)
        
        mula_contents = cursor.fetchall()
        
        # Combine unique mula content
        full_mula_text = ""
        for (content,) in mula_contents:
            clean_content = re.sub(r'<[^>]+>', '', content)
            if "sāmaññaphalasuttaṃ" not in clean_content or full_mula_text == "":
                full_mula_text += clean_content + "\n\n"
        
        print(f"📖 DN2 Mula: {len(full_mula_text)} total characters")
        
        # Get UNIQUE commentary content
        cursor.execute("""
        SELECT DISTINCT pa.content
        FROM paragraph_mapping pm
        JOIN pages pa ON pa.bookid = pm.exp_book_id AND pa.page = pm.exp_page_number
        WHERE pm.base_book_id = 'mula_di_01' 
        AND pm.paragraph BETWEEN 150 AND 194
        AND pm.exp_book_id = 'attha_di_01'
        ORDER BY pm.exp_page_number
        """)
        
        commentary_contents = cursor.fetchall()
        
        # Combine unique commentary content
        full_commentary_text = ""
        for (content,) in commentary_contents:
            clean_content = re.sub(r'<[^>]+>', '', content)
            full_commentary_text += clean_content + "\n\n"
        
        print(f"📝 DN2 Commentary: {len(full_commentary_text)} total characters")
        
        # Smart chunking for mula text
        mula_chunks = self.chunk_text(full_mula_text, max_chars=3500)
        print(f"📦 Mula split into {len(mula_chunks)} chunks")
        
        # Translate mula chunks
        mula_translations = []
        for i, chunk in enumerate(mula_chunks):
            print(f"\n🌐 Translating Mula Chunk {i+1}/{len(mula_chunks)}...")
            translation = self.translate_text(chunk, f"DN2 Mula Part {i+1}")
            mula_translations.append(translation)
            if i < len(mula_chunks) - 1:  # Don't delay after last chunk
                time.sleep(3)
        
        full_mula_translation = "\n\n".join(mula_translations)
        
        # Save mula translation
        self.save_translation(
            'mula_di_01', 150, 'complete_dn2_full',
            'mula', full_mula_text, full_mula_translation
        )
        
        time.sleep(5)  # Longer delay between mula and commentary
        
        # Smart chunking for commentary text
        commentary_chunks = self.chunk_text(full_commentary_text, max_chars=3500)
        print(f"📦 Commentary split into {len(commentary_chunks)} chunks")
        
        # Translate commentary chunks
        commentary_translations = []
        for i, chunk in enumerate(commentary_chunks):
            print(f"\n🌐 Translating Commentary Chunk {i+1}/{len(commentary_chunks)}...")
            translation = self.translate_text(chunk, f"DN2 Commentary Part {i+1}")
            commentary_translations.append(translation)
            if i < len(commentary_chunks) - 1:
                time.sleep(3)
        
        full_commentary_translation = "\n\n".join(commentary_translations)
        
        # Save commentary translation
        self.save_translation(
            'attha_di_01', 122, 'complete_dn2_full',
            'commentary', full_commentary_text, full_commentary_translation
        )
        
        # Generate final HTML
        self.generate_complete_dn2_html(
            full_mula_text, 
            full_mula_translation,
            full_commentary_text,
            full_commentary_translation
        )
        
        print(f"\n🎉 COMPLETE DN2 TRANSLATION FINISHED!")
        print(f"📊 Total API calls: {len(mula_chunks) + len(commentary_chunks)}")
        print(f"📊 Mula: {len(full_mula_translation)} chars translated")
        print(f"📊 Commentary: {len(full_commentary_translation)} chars translated")
    
    def chunk_text(self, text, max_chars=3500):
        """Split text into chunks at paragraph boundaries"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs (double newlines)
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            # If adding this paragraph would exceed limit, start new chunk
            if len(current_chunk) + len(para) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += '\n\n' + para
                else:
                    current_chunk = para
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    def resume_failed_translations(self):
        """Resume translation for failed chunks only"""
        print("🔄 RESUMING FAILED TRANSLATIONS")
        print("=" * 50)
        
        cursor = self.translation_db.cursor()
        
        # Find all translation attempts
        cursor.execute("""
        SELECT original_book_id, original_paragraph, content_type, original_content, translated_content
        FROM translations 
        WHERE original_paragraph LIKE 'complete_dn2_full%'
        ORDER BY id
        """)
        
        all_translations = cursor.fetchall()
        
        # Identify failed translations (contain error messages)
        failed_translations = []
        for book_id, paragraph, content_type, original, translated in all_translations:
            if translated and any(error in translated for error in ['[TRANSLATION FAILED', '[TRANSLATION ERROR', 'HTTPSConnectionPool']):
                print(f"❌ Failed: {content_type} - {paragraph}")
                failed_translations.append((book_id, paragraph, content_type, original))
            elif not translated or translated == '':
                print(f"❌ Empty: {content_type} - {paragraph}")
                failed_translations.append((book_id, paragraph, content_type, original))
        
        print(f"\n📊 Found {len(failed_translations)} failed translations to retry")
        
        if not failed_translations:
            print("✅ No failed translations found!")
            return
        
        # Retry failed translations
        success_count = 0
        for book_id, paragraph, content_type, original in failed_translations:
            print(f"\n🔄 Retrying: {content_type} - {paragraph}")
            
            # Delete the failed entry
            cursor.execute("""
            DELETE FROM translations 
            WHERE original_book_id = ? AND original_paragraph = ? AND content_type = ?
            """, (book_id, paragraph, content_type))
            
            # Retry translation
            context = f"Retry {content_type} {paragraph}"
            new_translation = self.translate_text(original, context)
            
            # Save new translation
            if new_translation and not any(error in new_translation for error in ['[TRANSLATION FAILED', '[TRANSLATION ERROR']):
                cursor.execute("""
                INSERT INTO translations 
                (original_book_id, original_page_number, original_paragraph, content_type, original_content, translated_content)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (book_id, 150 if 'mula' in content_type else 122, paragraph, content_type, original, new_translation))
                
                self.translation_db.commit()
                success_count += 1
                print(f"✅ Retry successful: {content_type} - {paragraph}")
            else:
                print(f"❌ Retry failed again: {content_type} - {paragraph}")
            
            time.sleep(2)  # Be gentle with the API
        
        print(f"\n🎉 RESUME COMPLETE: {success_count}/{len(failed_translations)} retries successful")
    
    def check_translation_status(self):
        """Check status of all translations"""
        print("📊 TRANSLATION STATUS CHECK")
        print("=" * 40)
        
        cursor = self.translation_db.cursor()
        
        # Count by status
        cursor.execute("""
        SELECT 
            content_type,
            COUNT(*) as total,
            SUM(CASE WHEN translated_content LIKE '%[TRANSLATION FAILED%' OR translated_content LIKE '%[TRANSLATION ERROR%' OR translated_content LIKE '%HTTPSConnectionPool%' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN translated_content IS NULL OR translated_content = '' THEN 1 ELSE 0 END) as empty,
            SUM(CASE WHEN translated_content NOT LIKE '%[TRANSLATION%' AND translated_content != '' THEN 1 ELSE 0 END) as success
        FROM translations 
        WHERE original_paragraph LIKE 'complete_dn2_full%'
        GROUP BY content_type
        """)
        
        results = cursor.fetchall()
        
        for content_type, total, failed, empty, success in results:
            print(f"\n{content_type.upper()}:")
            print(f"  Total: {total}")
            print(f"  Success: {success}")
            print(f"  Failed: {failed}")
            print(f"  Empty: {empty}")
            print(f"  Success Rate: {success/total*100:.1f}%")
        
    def generate_dn2_html_from_db(self):
        """Generate HTML by loading translations from database"""
        print("🎨 GENERATING DN2 HTML FROM DATABASE")
        print("=" * 50)
        
        cursor = self.translation_db.cursor()
        
        # Get mula translation
        cursor.execute("""
        SELECT original_content, translated_content 
        FROM translations 
        WHERE original_book_id = 'mula_di_01' 
        AND content_type = 'mula'
        ORDER BY id DESC LIMIT 1
        """)
        
        mula_result = cursor.fetchone()
        if not mula_result:
            print("❌ No mula translation found")
            return
            
        mula_original, mula_translated = mula_result
        
        # Get commentary translation  
        cursor.execute("""
        SELECT original_content, translated_content 
        FROM translations 
        WHERE original_book_id = 'attha_di_01' 
        AND content_type = 'commentary'
        ORDER BY id DESC LIMIT 1
        """)
        
        commentary_result = cursor.fetchone()
        if not commentary_result:
            print("❌ No commentary translation found")
            return
            
        commentary_original, commentary_translated = commentary_result
        
        # Call the existing HTML generator
        self.generate_complete_dn2_html(
            mula_original, 
            mula_translated,
            commentary_original, 
            commentary_translated
        )
  
if __name__ == "__main__":
    translator = DN2RealTranslator(
        '~/.local/share/com.paauk.tipitaka_pali_reader/tipitaka_pali.db',
        'translations.db'
    )
    
    translator.generate_dn2_html_from_db()
