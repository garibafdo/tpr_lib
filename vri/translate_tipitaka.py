import json
import requests
from tqdm import tqdm
import time
import os

class TipitakaTranslator:
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.translated_data = []
        self.translation_cache = {}  # For resuming interrupted translations
        
    def load_translation_pairs(self):
        """Load the translation pairs JSON"""
        with open('translation_pairs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_existing_translations(self, output_file: str):
        """Load already translated data to resume"""
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                self.translated_data = json.load(f)
            print(f"📂 Resumed with {len(self.translated_data)} existing translations")
            
            # Create cache for quick lookup
            self.translation_cache = {item['paragraph_number']: True for item in self.translated_data}
            
    def translate_all(self, output_file: str = "translated_texts.json", batch_size: int = 10):
        """Translate all texts with clean progress tracking"""
        pairs = self.load_translation_pairs()
        self.load_existing_translations(output_file)
        
        pending_pairs = [p for p in pairs if p['paragraph_number'] not in self.translation_cache]
        
        if not pending_pairs:
            print("✅ All translations already completed!")
            return
        
        print(f"🔄 Translating {len(pending_pairs)} paragraphs...")
        
        with tqdm(total=len(pending_pairs), desc="Overall", unit="para") as main_bar:
            for i, pair in enumerate(pending_pairs):
                para_num = pair['paragraph_number']
                
                # Update main progress bar description
                main_bar.set_description(f"📖 Para {para_num}")
                
                # Translate with nested progress
                mula_english = self.translate_text(
                    pair['mula_text'], 
                    f"Mula {para_num}", 
                    main_bar
                )
                
                commentary_english = ""
                if pair['has_commentary'] and pair['commentary_text']:
                    commentary_english = self.translate_text(
                        pair['commentary_text'],
                        f"Comm {para_num}", 
                        main_bar
                    )
                
                # Add to results
                translated_item = {
                    'paragraph_number': para_num,
                    'sutta': pair['sutta'],
                    'mula_pali': pair['mula_text'],
                    'mula_english': mula_english,
                    'commentary_pali': pair['commentary_text'],
                    'commentary_english': commentary_english,
                    'has_commentary': pair['has_commentary']
                }
                
                self.translated_data.append(translated_item)
                
                # Save progress periodically
                if (i + 1) % batch_size == 0:
                    self._save_progress(output_file)
                    main_bar.set_description(f"💾 Saved {i+1}")
                
                main_bar.update(1)
                time.sleep(1)  # Respectful delay
        
        self._save_progress(output_file)
        print(f"✅ Complete! {len(self.translated_data)} paragraphs in {output_file}")
    def translate_text(self, text, context="", progress_bar=None):
        """Translate text with minimal output, using tqdm"""
        if not text.strip():
            return ""
        
        if progress_bar:
            progress_bar.set_description(f"🌐 {context}")
        
        payload = {
            'input_sentence': text,
            'input_encoding': 'auto', 
            'target_lang': 'english',
            'do_grammar_explanation': False,
            'model': 'default'
        }
        
        try:
            response = requests.post(
                "https://dharmamitra.org/next/api/mitra-translation-stream",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=120,
                stream=True
            )
            
            if response.status_code == 200:
                full_response = ""
                with tqdm(total=len(text), desc="Receiving", unit="char", 
                         leave=False, mininterval=0.5) as pbar:
                    for chunk in response.iter_content(decode_unicode=True, chunk_size=100):
                        if chunk:
                            chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                            full_response += chunk_text
                            pbar.update(len(chunk_text))
                
                return full_response.strip()
            else:
                return f"[API Error: {response.status_code}]"
                
        except Exception as e:
            return f"[Error: {e}]"
    # ~ def translate_text(self, text, context=""):
        # ~ """Translate text with streaming progress"""
        # ~ if not text.strip():
            # ~ return ""
            
        # ~ print(f"🌐 Translating: {context}")
        # ~ print(f"   📝 Text length: {len(text)} characters")
        
        # ~ payload = {
            # ~ 'input_sentence': text,
            # ~ 'input_encoding': 'auto', 
            # ~ 'target_lang': 'english',
            # ~ 'do_grammar_explanation': False,
            # ~ 'model': 'default'
        # ~ }
        
        # ~ try:
            # ~ print("   📤 Sending request...", end="", flush=True)
            # ~ response = requests.post(
                # ~ "https://dharmamitra.org/next/api/mitra-translation-stream",
                # ~ headers={'Content-Type': 'application/json'},
                # ~ data=json.dumps(payload),
                # ~ timeout=120,
                # ~ stream=True
            # ~ )
            
            # ~ if response.status_code == 200:
                # ~ print(" ✅ Request accepted", end="", flush=True)
                
                # ~ full_response = ""
                # ~ with tqdm(total=len(text), desc="Receiving", unit="char", leave=False) as pbar:
                    # ~ for chunk in response.iter_content(decode_unicode=True, chunk_size=100):
                        # ~ if chunk:
                            # ~ chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                            # ~ full_response += chunk_text
                            # ~ pbar.update(len(chunk_text))
                
                # ~ translation = full_response.strip()
                # ~ print(f"\r   ✅ Translation complete: {len(translation)} characters")
                # ~ return translation
                
            # ~ else:
                # ~ print(f"\n❌ API error: {response.status_code}")
                # ~ return f"[TRANSLATION FAILED: {response.status_code}]"
                
        # ~ except Exception as e:
            # ~ print(f"\n❌ Request failed: {e}")
            # ~ return f"[TRANSLATION ERROR: {e}]"
    
    # ~ def translate_all(self, output_file: str = "translated_texts.json", batch_size: int = 10):
        # ~ """Translate all texts with progress tracking"""
        # ~ pairs = self.load_translation_pairs()
        # ~ self.load_existing_translations(output_file)
        
        # ~ # Filter out already translated paragraphs
        # ~ pending_pairs = [p for p in pairs if p['paragraph_number'] not in self.translation_cache]
        
        # ~ if not pending_pairs:
            # ~ print("✅ All translations already completed!")
            # ~ return
        
        # ~ print(f"🔄 Starting translation of {len(pending_pairs)} paragraphs...")
        
        # ~ with tqdm(total=len(pending_pairs), desc="Overall Progress") as pbar:
            # ~ for i, pair in enumerate(pending_pairs):
                # ~ para_num = pair['paragraph_number']
                # ~ sutta_name = pair['sutta']
                
                # ~ print(f"\n📖 Paragraph {para_num} ({sutta_name})")
                
                # ~ # Translate mula text
                # ~ mula_context = f"Mula {para_num}"
                # ~ mula_english = self.translate_text(pair['mula_text'], mula_context)
                
                # ~ # Translate commentary text if exists
                # ~ commentary_english = ""
                # ~ if pair['has_commentary'] and pair['commentary_text']:
                    # ~ commentary_context = f"Commentary {para_num}"
                    # ~ commentary_english = self.translate_text(pair['commentary_text'], commentary_context)
                
                # ~ # Add to results
                # ~ translated_item = {
                    # ~ 'paragraph_number': para_num,
                    # ~ 'sutta': sutta_name,
                    # ~ 'mula_pali': pair['mula_text'],
                    # ~ 'mula_english': mula_english,
                    # ~ 'commentary_pali': pair['commentary_text'],
                    # ~ 'commentary_english': commentary_english,
                    # ~ 'has_commentary': pair['has_commentary']
                # ~ }
                
                # ~ self.translated_data.append(translated_item)
                
                # ~ # Save progress every batch_size items
                # ~ if (i + 1) % batch_size == 0:
                    # ~ self._save_progress(output_file)
                    # ~ print(f"💾 Progress saved after {i + 1} paragraphs")
                
                # ~ pbar.update(1)
                
                # ~ # Small delay to be respectful to API
                # ~ time.sleep(1)
        
        # ~ # Final save
        # ~ self._save_progress(output_file)
        # ~ print(f"✅ Translation complete! Saved {len(self.translated_data)} paragraphs to {output_file}")
    
    def _save_progress(self, output_file: str):
        """Save current progress to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.translated_data, f, ensure_ascii=False, indent=2)


    def translate_test(self, test_sutta: str = "1. Brahmajālasuttaṃ", max_paragraphs: int = 3, 
                      output_file: str = "test_translations.json", dry_run: bool = False):
        """Test translation with limited scope"""
        pairs = self.load_translation_pairs()
        
        # Filter for specific sutta and limit paragraphs
        test_pairs = [p for p in pairs if p['sutta'] == test_sutta][:max_paragraphs]
        
        if not test_pairs:
            print(f"❌ No paragraphs found for sutta: {test_sutta}")
            return
        
        print(f"🧪 TEST MODE: Translating {len(test_pairs)} paragraphs from {test_sutta}")
        
        if dry_run:
            print("🔍 DRY RUN - Checking data structure:")
            for i, pair in enumerate(test_pairs):
                print(f"  {i+1}. Para {pair['paragraph_number']}: "
                      f"Mula({len(pair['mula_text'])} chars), "
                      f"Commentary({len(pair['commentary_text'])} chars)")
            return
        
        self.translated_data = []  # Start fresh for test
        
        for i, pair in enumerate(test_pairs):
            para_num = pair['paragraph_number']
            
            print(f"\n📖 TEST Paragraph {para_num}")
            print(f"   Mula: {pair['mula_text'][:100]}...")
            
            if pair['has_commentary']:
                print(f"   Commentary: {pair['commentary_text'][:100]}...")
            
            # Translate mula text
            mula_english = self.translate_text(pair['mula_text'], f"TEST Mula {para_num}")
            
            # Translate commentary if exists
            commentary_english = ""
            if pair['has_commentary'] and pair['commentary_text']:
                commentary_english = self.translate_text(pair['commentary_text'], f"TEST Commentary {para_num}")
            
            # Add to results
            translated_item = {
                'paragraph_number': para_num,
                'sutta': pair['sutta'],
                'mula_pali': pair['mula_text'],
                'mula_english': mula_english,
                'commentary_pali': pair['commentary_text'],
                'commentary_english': commentary_english,
                'has_commentary': pair['has_commentary']
            }
            
            self.translated_data.append(translated_item)
            
            # Save after each paragraph for testing
            self._save_progress(output_file)
            print(f"💾 Test progress saved: {i+1}/{len(test_pairs)}")
        
        print(f"✅ TEST COMPLETE! Saved {len(self.translated_data)} paragraphs to {output_file}")

# ~ def main():
    # ~ translator = TipitakaTranslator()
    
    # ~ print("Tipiṭaka Translation TEST System")
    # ~ print("=" * 50)
    
    # ~ # Test sequence:
    
    # ~ # 1. Dry run - just check data structure
    # ~ print("\n1. 🧪 DRY RUN - Data verification:")
    # ~ translator.translate_test(dry_run=True, max_paragraphs=2)
    
    # ~ # 2. Small test - actual translation
    # ~ print("\n2. 🧪 SMALL TEST - Actual translation:")
    # ~ translator.translate_test(max_paragraphs=2)
    
    # 3. If successful, run full DN1 test
    # Uncomment after verifying small test works:
    # print("\n3. 🧪 FULL DN1 TEST:")
    # translator.translate_test(max_paragraphs=10)
    
def main():
    """Run the translation process"""
    translator = TipitakaTranslator()
    
    print("Tipiṭaka Translation System")
    print("=" * 50)
    
    # Translate all texts
    translator.translate_all("translated_texts.json")

if __name__ == "__main__":
    main()
