#!/usr/bin/env python3
"""
Tipiṭaka Sutta and Paragraph Mapping Script
Creates two-layer mapping: Sutta->Paragraphs and Paragraph->Commentary
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import List, Dict, Any, Tuple

class TipitakaMapper:
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.sutta_structure = {}  # sutta_name -> {paragraphs: [], files: []}
        self.paragraph_texts = {}  # para_number -> {mula_text: "", commentary_text: ""}
        self.current_sutta = None
        self.current_para_range = [None, None]
    
    def extract_sutta_info(self, xml_file: str) -> Tuple[str, str]:
        """Extract sutta number and name from chapter title"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Look for chapter title
            for p in root.findall('.//p'):
                if p.get('rend') == 'chapter':
                    title_text = ''.join(p.itertext()).strip()
                    
                    # Parse patterns like "11. Kevaṭṭasuttaṃ" or "11. Kevaṭṭasuttavaṇṇanā"
                    match = re.match(r'(\d+)\.\s+(.+)', title_text)
                    if match:
                        sutta_num = match.group(1)
                        sutta_name = match.group(2)
                        
                        # Normalize names (remove 'vaṇṇanā' from commentary)
                        base_name = re.sub(r'vaṇṇanā$', '', sutta_name).strip()
                        base_name = re.sub(r'suttavaṇṇanā$', 'sutta', base_name).strip()
                        
                        return sutta_num, base_name
            
            return None, None
            
        except Exception as e:
            print(f"Error extracting sutta info from {xml_file}: {e}")
            return None, None
    
    def parse_mula_file(self, xml_file: str):
        """Parse mūla file to extract sutta structure and paragraph texts"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get sutta info
            sutta_num, sutta_name = self.extract_sutta_info(xml_file)
            if not sutta_num:
                print(f"Could not extract sutta info from {xml_file}")
                return
            
            sutta_key = f"{sutta_num}. {sutta_name}"
            
            if sutta_key not in self.sutta_structure:
                self.sutta_structure[sutta_key] = {
                    'paragraphs': [],
                    'files': [],
                    'type': 'mula'
                }
            
            self.sutta_structure[sutta_key]['files'].append(xml_file)
            
            # Extract paragraphs
            current_para = None
            for p in root.findall('.//p'):
                rend = p.get('rend', '')
                para_num = p.get('n', '').strip()
                text = ''.join(p.itertext()).strip()
                
                if not text:
                    continue
                
                # Skip chapter and subhead for paragraph collection
                if rend in ['chapter', 'subhead']:
                    continue
                
                # Handle numbered paragraphs
                if para_num:
                    current_para = para_num
                    self.sutta_structure[sutta_key]['paragraphs'].append(para_num)
                    
                    # Store paragraph text
                    if para_num not in self.paragraph_texts:
                        self.paragraph_texts[para_num] = {'mula_text': '', 'commentary_text': ''}
                    self.paragraph_texts[para_num]['mula_text'] = text
                    self.paragraph_texts[para_num]['sutta'] = sutta_key
                
                # Handle continuation paragraphs (no number)
                elif current_para and rend == 'bodytext':
                    # Append to current paragraph
                    if current_para in self.paragraph_texts:
                        self.paragraph_texts[current_para]['mula_text'] += ' ' + text
            
        except Exception as e:
            print(f"Error parsing mūla file {xml_file}: {e}")
    
      
            
    def load_all_data(self):
        """Load all mūla and commentary files"""
        print("Loading XML files...")
        
        # First pass: Load all mūla files to establish structure
        mula_files = [f for f in os.listdir(self.data_dir) 
                     if f.startswith('s01') and 'm.mul' in f and f.endswith('.xml')]
        
        for filename in mula_files:
            file_path = os.path.join(self.data_dir, filename)
            self.parse_mula_file(file_path)
        
        # Second pass: Load commentary files
        commentary_files = [f for f in os.listdir(self.data_dir) 
                           if f.startswith('s01') and 'a.att' in f and f.endswith('.xml')]
        
        for filename in commentary_files:
            file_path = os.path.join(self.data_dir, filename)
            self.parse_commentary_file(file_path)
        
        print(f"Loaded {len(self.sutta_structure)} suttas")
        print(f"Loaded {len(self.paragraph_texts)} paragraphs")
    
    def generate_mappings(self) -> Dict[str, Any]:
        """Generate both sutta and paragraph mappings"""
        
        # Sutta mapping
        sutta_mapping = {}
        for sutta_name, sutta_info in self.sutta_structure.items():
            # Remove duplicates and sort paragraphs
            unique_paras = sorted(set(sutta_info['paragraphs']), 
                                 key=lambda x: int(x) if x.isdigit() else float('inf'))
            
            sutta_mapping[sutta_name] = {
                'paragraphs': unique_paras,
                'files': sutta_info['files'],
                'paragraph_count': len(unique_paras)
            }
        
        # Paragraph mapping with sutta context
        paragraph_mapping = {}
        for para_num, para_info in self.paragraph_texts.items():
            paragraph_mapping[para_num] = {
                'sutta': para_info.get('sutta', 'Unknown'),
                'mula_text': para_info['mula_text'],
                'commentary_text': para_info['commentary_text'],
                'has_commentary': bool(para_info['commentary_text'])
            }
        
        return {
            'sutta_mapping': sutta_mapping,
            'paragraph_mapping': paragraph_mapping
        }
    
    def generate_translation_pairs(self) -> List[Dict[str, Any]]:
        """Generate pairs for AI translation with sutta context"""
        pairs = []
        
        for sutta_name, sutta_info in self.sutta_structure.items():
            for para_num in sorted(set(sutta_info['paragraphs']), 
                                  key=lambda x: int(x) if x.isdigit() else float('inf')):
                
                if para_num in self.paragraph_texts:
                    para_info = self.paragraph_texts[para_num]
                    
                    pairs.append({
                        'sutta': sutta_name,
                        'paragraph_number': para_num,
                        'mula_text': para_info['mula_text'],
                        'commentary_text': para_info['commentary_text'],
                        'has_commentary': bool(para_info['commentary_text'])
                    })
        
        return pairs
    
    def save_mappings(self):
        """Save all mappings to JSON files"""
        mappings = self.generate_mappings()
        pairs = self.generate_translation_pairs()
        
        # Save sutta mapping
        with open('sutta_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mappings['sutta_mapping'], f, ensure_ascii=False, indent=2)
        
        # Save paragraph mapping
        with open('paragraph_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mappings['paragraph_mapping'], f, ensure_ascii=False, indent=2)
        
        # Save translation pairs
        with open('translation_pairs.json', 'w', encoding='utf-8') as f:
            json.dump(pairs, f, ensure_ascii=False, indent=2)
        
        # Print statistics
        total_paras = len(pairs)
        paras_with_commentary = sum(1 for p in pairs if p['has_commentary'])
        
        print(f"\n=== MAPPING COMPLETE ===")
        print(f"Suttas mapped: {len(mappings['sutta_mapping'])}")
        print(f"Paragraphs total: {total_paras}")
        print(f"Paragraphs with commentary: {paras_with_commentary}")
        print(f"Coverage: {paras_with_commentary/total_paras*100:.1f}%")
        print(f"\nFiles saved:")
        print(f"- sutta_mapping.json: Sutta -> Paragraph ranges")
        print(f"- paragraph_mapping.json: Paragraph -> Texts")
        print(f"- translation_pairs.json: Ready for AI translation")
        
        return mappings, pairs
    
    def print_sample(self, count: int = 3):
            """Print sample mappings for verification"""
            pairs = self.generate_translation_pairs()
            
            print(f"\n=== SAMPLE MAPPINGS (first {count} suttas) ===")
            
            current_sutta = None
            printed = 0
            
            for pair in pairs:
                if pair['sutta'] != current_sutta:
                    if printed >= count:
                        break
                    current_sutta = pair['sutta']
                    printed += 1
                    print(f"\n┌── {current_sutta} ──")
                
                commentary_indicator = "✓" if pair['has_commentary'] else "✗"
                print(f"│ {pair['paragraph_number']} [{commentary_indicator}] {pair['mula_text'][:80]}...")

    def parse_commentary_file(self, xml_file: str):
        """Parse commentary file to extract commentary texts"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            sutta_num, sutta_name = self.extract_sutta_info(xml_file)
            if not sutta_num:
                return
            
            sutta_key = f"{sutta_num}. {sutta_name}"
            
            # Process all paragraphs in order to handle continuation
            current_section = None
            current_text = []
            
            for p in root.findall('.//p'):
                rend = p.get('rend', '')
                para_num = p.get('n', '').strip()
                text = ''.join(p.itertext()).strip()
                
                if not text or rend in ['chapter', 'subhead']:
                    continue
                
                # If we hit a new numbered paragraph, save previous section
                if para_num and current_section:
                    self._apply_commentary_text(current_section, current_text, sutta_key)
                    current_section = None
                    current_text = []
                
                # Start new section if numbered paragraph
                if para_num:
                    current_section = para_num
                    current_text = [text]
                # Continue current section if bodytext
                elif rend == 'bodytext' and current_section:
                    current_text.append(text)
            
            # Don't forget the last section
            if current_section:
                self._apply_commentary_text(current_section, current_text, sutta_key)
            
        except Exception as e:
            print(f"Error parsing commentary file {xml_file}: {e}")

    def _apply_commentary_text(self, para_num: str, text_parts: List[str], sutta_key: str):
        """Apply complete commentary text to paragraph mapping"""
        full_text = ' '.join(text_parts)
        
        if '-' in para_num:
            start_end = para_num.split('-')
            if len(start_end) == 2:
                try:
                    start, end = int(start_end[0]), int(start_end[1])
                    for para in range(start, end + 1):
                        self._add_commentary_to_paragraph(str(para), full_text, sutta_key)
                    return
                except ValueError:
                    pass
        
        self._add_commentary_to_paragraph(para_num, full_text, sutta_key)

    def _add_commentary_to_paragraph(self, para_num: str, text: str, sutta_key: str):
        """Add commentary text to specific paragraph"""
        if para_num not in self.paragraph_texts:
            self.paragraph_texts[para_num] = {'mula_text': '', 'commentary_text': '', 'sutta': sutta_key}
        
        if self.paragraph_texts[para_num]['commentary_text']:
            self.paragraph_texts[para_num]['commentary_text'] += ' ' + text
        else:
            self.paragraph_texts[para_num]['commentary_text'] = text
               
def main():
    """Main execution"""
    mapper = TipitakaMapper()
    
    print("Tipiṭaka Mapping System")
    print("=" * 50)
    
    # Load data
    mapper.load_all_data()
    
    # Generate and save mappings
    mappings, pairs = mapper.save_mappings()
    
    # Show samples
    mapper.print_sample(3)
    
    print(f"\nDone! Use the generated JSON files for your AI translation pipeline.")

if __name__ == "__main__":
    main()
