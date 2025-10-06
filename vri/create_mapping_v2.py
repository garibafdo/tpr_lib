#!/usr/bin/env python3
"""
Improved XML to JSON mapping for Tipiṭaka texts
Version 2 - Preserves original JSON structure with bug fixes
Outputs separate files for DN2 vagga to avoid overwriting DN1 data
"""

import os
import re
import json
import glob
from bs4 import BeautifulSoup

def extract_sutta_name(xml_content):
    """Extract sutta name from XML content"""
    soup = BeautifulSoup(xml_content, 'xml')
    chapter_elem = soup.find('p', {'rend': 'chapter'})
    if chapter_elem:
        return chapter_elem.get_text().strip()
    return "Unknown Sutta"

def parse_paragraphs_preserving_structure(xml_content):
    """
    Parse XML content while properly handling paragraph boundaries
    Returns list of paragraphs with proper text extraction
    """
    paragraphs = []
    
    soup = BeautifulSoup(xml_content, 'xml')
    all_elements = soup.find_all(['p', 'hi', 'pb', 'note'])
    
    current_para = None
    current_para_number = None
    current_content = []
    
    for element in all_elements:
        # Skip direct children of current paragraph (avoid duplicates)
        if current_para and element in current_para.find_all(recursive=False):
            continue
            
        # Check if this is a new numbered paragraph
        if element.name == 'p' and element.get('rend') == 'bodytext' and element.get('n'):
            # Save previous paragraph if exists
            if current_para_number is not None and current_content:
                # ~ para_text = ' '.join([elem.get_text().strip() for elem in current_content if elem.get_text().strip()])
                para_text = ' '.join([str(elem) for elem in current_content])  # Keep XML tags

                if para_text:
                    paragraphs.append({
                        'paragraph_number': current_para_number,
                        'text': para_text
                    })
            
            # Start new paragraph
            current_para = element
            current_para_number = element.get('n')
            current_content = [element]
            
        elif element.name == 'p' and current_para_number is not None:
            # Continuation paragraph (subhead, gatha, etc.) - only if no 'n' attribute
            if not element.get('n'):
                current_content.append(element)
                
        elif current_para_number is not None:
            # Other elements within current paragraph
            current_content.append(element)
    
    # Save the last paragraph
    if current_para_number is not None and current_content:
        # ~ para_text = ' '.join([elem.get_text().strip() for elem in current_content if elem.get_text().strip()])
        para_text = ' '.join([str(elem) for elem in current_content])  # Keep XML tags
        if para_text:
            paragraphs.append({
                'paragraph_number': current_para_number,
                'text': para_text
            })
    
    return paragraphs

def process_vagga_files(sutta_prefix, output_prefix):
    """
    Process all mula and commentary files for a given sutta prefix
    Outputs separate files to avoid overwriting DN1 data
    """
    sutta_mapping = {}
    paragraph_mapping = {}
    translation_pairs = []
    
    # Process both mula and commentary files
    file_types = [
        ('m', 'mul'),  # Mūla files
        ('a', 'att')   # Commentary files
    ]
    
    for file_type, file_code in file_types:
        file_pattern = f"xml_files/{sutta_prefix}*{file_type}.{file_code}*.xml"
        xml_files = glob.glob(file_pattern)
        
        if not xml_files:
            print(f"No {file_code} files found matching: {file_pattern}")
            continue
            
        # Sort files numerically
        xml_files.sort(key=lambda x: int(re.search(rf'{file_code}(\d+)', x).group(1)) 
                      if re.search(rf'{file_code}(\d+)', x) else 0)
        
        print(f"Processing {len(xml_files)} {file_code} files for prefix {sutta_prefix}...")
        
        for xml_file in xml_files:
            try:
                # Try different encodings
                for encoding in ['utf-16', 'utf-8-sig', 'latin-1']:
                    try:
                        with open(xml_file, 'r', encoding=encoding) as f:
                            xml_content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"  Could not decode {xml_file}")
                    continue
                
                # Extract sutta name (use first mula file for mapping)
                if file_type == 'm':
                    sutta_name = extract_sutta_name(xml_content)
                    file_key = os.path.basename(xml_file).replace('.xml', '')
                
                # Parse paragraphs
                paragraphs = parse_paragraphs_preserving_structure(xml_content)
                
                for para in paragraphs:
                    para_num = para['paragraph_number']
                    
                    # Build translation pairs
                    if file_type == 'm':
                        # Mūla text - create new entry
                        translation_pairs.append({
                            'sutta': sutta_name,
                            'paragraph_number': para_num,
                            'mula_text': para['text'],
                            'commentary_text': "",
                            'has_commentary': False
                        })
                    else:
                        # Commentary text - find and update existing entry
                        for pair in translation_pairs:
                            if pair['paragraph_number'] == para_num:
                                pair['commentary_text'] = para['text']
                                pair['has_commentary'] = True
                                break
                
                print(f"  Processed {xml_file}: {len(paragraphs)} paragraphs")
                
            except Exception as e:
                print(f"  Error processing {xml_file}: {e}")
    
    # Build correct JSON structures
    sutta_data = {}
    para_data = {}
    
    # Build sutta_mapping
    for pair in translation_pairs:
        sutta_name = pair['sutta']
        if sutta_name not in sutta_data:
            sutta_data[sutta_name] = {
                'paragraphs': [],
                'files': [f"{sutta_prefix}*.xml"],  # Simplified file list
                'paragraph_count': 0
            }
        
        if pair['paragraph_number'] not in sutta_data[sutta_name]['paragraphs']:
            sutta_data[sutta_name]['paragraphs'].append(pair['paragraph_number'])
            sutta_data[sutta_name]['paragraph_count'] += 1
    
    # Sort paragraphs numerically
    for sutta in sutta_data.values():
        sutta['paragraphs'].sort(key=int)
    
    # Build paragraph_mapping
    for pair in translation_pairs:
        para_data[pair['paragraph_number']] = {
            'sutta': pair['sutta'],
            'mula_text': pair['mula_text'],
            'commentary_text': pair['commentary_text'],
            'has_commentary': pair['has_commentary']
        }
    
    # Save to separate files for DN2 vagga
    with open(f"{output_prefix}_sutta_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(sutta_data, f, ensure_ascii=False, indent=2)
    
    with open(f"{output_prefix}_paragraph_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(para_data, f, ensure_ascii=False, indent=2)
    
    with open(f"{output_prefix}_translation_pairs.json", 'w', encoding='utf-8') as f:
        json.dump(translation_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"\nDN2 Vagga processing complete!")
    print(f"Total translation pairs: {len(translation_pairs)}")
    print(f"Output files: {output_prefix}_*.json")
    
def main():
    """Process DN2 vagga (s02 series)"""
    sutta_prefix = "s0102"  # DN2 vagga (DN14-DN23)
    output_prefix = "dn2_vagga"  # Separate from DN1 files
    
    process_vagga_files(sutta_prefix, output_prefix)

if __name__ == "__main__":
    main()
