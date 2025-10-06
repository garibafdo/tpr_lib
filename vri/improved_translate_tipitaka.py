#!/usr/bin/env python3
"""
Improved Tipiṭaka Translation Script
- Respectful API usage with rate limiting
- Smart resume/retry for failed translations  
- Better progress tracking with tqdm
"""

import os,sys
import json
import time
import requests
from tqdm import tqdm
from typing import List, Dict, Any
prefix = sys.argv[1] if len(sys.argv) > 1 else ""

class ImprovedTipitakaTranslator:
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.translated_data = []
        self.translation_cache = {}
    
    def load_translation_pairs(self) -> List[Dict]:
        """Load the translation pairs JSON"""
        with open(f'{prefix}translation_pairs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_existing_translations(self, output_file: str):
        """Load already translated data to resume"""
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                self.translated_data = json.load(f)
            print(f"📂 Resumed with {len(self.translated_data)} existing translations")
            
            # Create cache for quick lookup
            self.translation_cache = {item['paragraph_number']: True for item in self.translated_data}
    
    def _needs_retranslation(self, para_num: str) -> bool:
        """Check if paragraph needs retranslation (both mula and commentary)"""
        if para_num not in self.translation_cache:
            return True
        
        existing = next((item for item in self.translated_data 
                        if item['paragraph_number'] == para_num), None)
        if not existing:
            return True
        
        # Check both fields for any error indicators
        mula_has_error = any(marker in existing.get('mula_english', '') 
                            for marker in ['[API Error', '[API Error: 502]', '[Error', '[Connection Error', '[Failed'])
        commentary_has_error = any(marker in existing.get('commentary_english', '') 
                                  for marker in ['[API Error', '[API Error: 502]', '[Error', '[Connection Error', '[Failed'])
        
        return mula_has_error or commentary_has_error
    
    def _update_translation(self, para_num: str, new_data: Dict):
        """Update existing translation or add new one"""
        for i, item in enumerate(self.translated_data):
            if item['paragraph_number'] == para_num:
                self.translated_data[i] = new_data
                return
        
        # If not found, add new
        self.translated_data.append(new_data)
    
    def translate_text(self, text: str, context: str = "", progress_bar = None, max_retries: int = 3) -> str:
        """Translate text with rate limiting and robust error handling"""
        # ~ time.sleep(3.5)
        if not text.strip():
            return ""
        
        # Rate limiting - minimum delay between requests
        time.sleep(3)
        
        for attempt in range(max_retries):
            try:
                if progress_bar:
                    progress_bar.set_description(f"🌐 {context} (Attempt {attempt+1})")
                
                payload = {
                    'input_sentence': text,
                    'input_encoding': 'auto', 
                    'target_lang': 'english',
                    'do_grammar_explanation': False,
                    'model': 'default'
                }
                
                response = requests.post(
                    "https://dharmamitra.org/next/api/mitra-translation-stream",
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(payload),
                    timeout=300,  # 5 minute timeout for long texts
                    stream=True
                )
                
                if response.status_code == 200:
                    full_response = ""
                    received_chars = 0
                    
                    for chunk in response.iter_content(decode_unicode=True, chunk_size=100):
                        if chunk:
                            chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                            full_response += chunk_text
                            received_chars += len(chunk_text)
                            if progress_bar:
                                progress_bar.set_description(f"📥 {context} ({received_chars}/{len(text)} chars)")
                    
                    return full_response.strip()
                    
                elif response.status_code == 429:
                    # Rate limited - exponential backoff
                    wait_time = 30 * (2 ** attempt)  # 30s, 60s, 120s
                    if progress_bar:
                        progress_bar.set_description(f"⏳ Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"[API Error: {response.status_code}]"
                    
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 30 * (2 ** attempt)
                    if progress_bar:
                        progress_bar.set_description(f"🔌 Connection failed, retry in {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"[Connection Error: {e}]"
            except Exception as e:
                return f"[Error: {e}]"
        
        return f"[Failed after {max_retries} attempts]"
    
    def translate_all(self, output_file: str = f'{prefix}translated_texts.json', batch_size: int = 10):
        """Translate all texts with clean progress and smart resume"""
        pairs = self.load_translation_pairs()
        self.load_existing_translations(output_file)
        
        # Smart filtering - only retry failed translations
        pending_pairs = [p for p in pairs if self._needs_retranslation(p['paragraph_number'])]
        
        if not pending_pairs:
            print("✅ All translations already completed successfully!")
            return
        
        print(f"🔄 Translating {len(pending_pairs)} paragraphs ({len(pairs)-len(pending_pairs)} already done)")
        
        with tqdm(total=len(pending_pairs), desc="Starting...", unit="para") as main_bar:
            for i, pair in enumerate(pending_pairs):
                para_num = pair['paragraph_number']
                sutta_name = pair['sutta'][:20]  # Truncate for display
                
                # Update main progress bar
                main_bar.set_description(f"📖 {para_num} ({sutta_name}...)")
                
                # Translate mula
                mula_english = self.translate_text(
                    pair['mula_text'], 
                    f"Mula {para_num}", 
                    main_bar
                )
                
                # Translate commentary if exists
                commentary_english = ""
                if pair['has_commentary'] and pair['commentary_text']:
                    commentary_english = self.translate_text(
                        pair['commentary_text'],
                        f"Comm {para_num}", 
                        main_bar
                    )
                
                # Update the existing record or add new
                self._update_translation(para_num, {
                    'paragraph_number': para_num,
                    'sutta': pair['sutta'],
                    'mula_pali': pair['mula_text'],
                    'mula_english': mula_english,
                    'commentary_pali': pair['commentary_text'],
                    'commentary_english': commentary_english,
                    'has_commentary': pair['has_commentary']
                })
                
                # Save progress
                if (i + 1) % batch_size == 0:
                    self._save_progress(output_file)
                    main_bar.set_description(f"💾 Saved {i+1}")
                
                main_bar.update(1)
            
            # Final save
            self._save_progress(output_file)
            main_bar.set_description(f"✅ Complete! {len(self.translated_data)} paragraphs")
    
    def _save_progress(self, output_file: str):
        """Save current progress to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.translated_data, f, ensure_ascii=False, indent=2)

def main():
    """Run the improved translation process"""
    translator = ImprovedTipitakaTranslator()
    
    print("Improved Tipiṭaka Translation System")
    print("=" * 50)
    print("Features: Rate limiting, Smart resume, Better progress tracking")
    print("=" * 50)
    
    # Translate all texts
    translator.translate_all(f'{prefix}translated_texts.json',batch_size=3)

if __name__ == "__main__":
    main()
