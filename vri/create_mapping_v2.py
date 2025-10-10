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
import xml.etree.ElementTree as ET

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
            
        # Check if this is a new numbered paragraph OR a sutta title
        if (element.name == 'p' and 
            ((element.get('rend') == 'bodytext' and element.get('n')) or 
             (element.get('rend') == 'subhead' and re.match(r'\d+\.\s+', element.get_text().strip())))):
            
            # Save previous paragraph if exists
            if current_para_number is not None and current_content:
                para_text = ' '.join([str(elem) for elem in current_content])
                if para_text:
                    paragraphs.append({
                        'paragraph_number': current_para_number,
                        'text': para_text
                    })
            
            # Start new paragraph
            current_para = element
            if element.get('rend') == 'subhead':
                # Sutta title gets special paragraph number
                current_para_number = f"sutta_title_{element.get_text().strip()}"
            else:
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
        para_text = ' '.join([str(elem) for elem in current_content])
        if para_text:
            paragraphs.append({
                'paragraph_number': current_para_number,
                'text': para_text
            })
    
    return paragraphs


def create_mapper_v2(xml_files):
    """Create mapping from XML files to sutta data - updated for MN"""
    mapper = {}
    
    for xml_file in xml_files:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Extract nikaya from filename (s0201 = MN, s0101 = DN, etc.)
        filename = xml_file.split('/')[-1]
        nikaya_code = filename[1:3]  # '02' for MN, '01' for DN
        
        if nikaya_code == '01':  # DN - existing logic
            # DN: 1 file = 1 sutta
            sutta_name = extract_sutta_name(xml_content)
            mapper[xml_file] = {
                'sutta': sutta_name, 
                'type': 'mula',
                'paragraphs': parse_paragraphs_preserving_structure(xml_content)
            }
            
        elif nikaya_code == '02':  # MN - new logic
            # MN: 1 file = multiple suttas
            sutta_titles = extract_mn_sutta_titles(xml_content)
            all_paragraphs = parse_paragraphs_preserving_structure(xml_content)
            
            # Group paragraphs by sutta
            sutta_paragraphs = group_paragraphs_by_sutta(all_paragraphs, sutta_titles)
            
            for sutta_title, paragraphs in sutta_paragraphs.items():
                unique_key = f"{xml_file}::{sutta_title}"
                mapper[unique_key] = {
                    'sutta': sutta_title,
                    'type': 'mula', 
                    'paragraphs': paragraphs,
                    'source_file': xml_file
                }
        else:
            # Fallback for other nikayas
            sutta_name = extract_sutta_name(xml_content)
            mapper[xml_file] = {
                'sutta': sutta_name,
                'type': 'mula',
                'paragraphs': parse_paragraphs_preserving_structure(xml_content)
            }
    
    return mapper


def extract_mn_sutta_titles(xml_content):
    """Extract all sutta titles from MN XML content"""
    sutta_titles = []
    
    # Parse XML content
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        # Try cleaning the XML if it has encoding issues
        xml_content = xml_content.replace('encoding="UTF-16"', 'encoding="UTF-8"')
        root = ET.fromstring(xml_content)
    
    # Find all p elements with rend="subhead"
    for p in root.findall('.//p[@rend="subhead"]'):
        text = p.text or ''
        # Only include subheads with numbers (sutta titles)
        if re.match(r'\d+\.\s+', text):
            sutta_titles.append(text)
    
    return sutta_titles

def group_paragraphs_by_sutta(paragraphs, sutta_titles):
    """Group paragraphs under their respective sutta titles"""
    sutta_paragraphs = {title: [] for title in sutta_titles}
    
    if not sutta_titles:
        return sutta_paragraphs
    
    current_sutta = sutta_titles[0]
    
    for para in paragraphs:
        para_text = para.get('text', '')
        
        # Check if this paragraph contains a sutta title
        for sutta_title in sutta_titles:
            if sutta_title in para_text:
                current_sutta = sutta_title
                # Don't add the title paragraph itself to content
                continue
        
        # Add regular paragraphs to current sutta
        if not para_text.startswith('sutta_title_'):
            sutta_paragraphs[current_sutta].append(para)
    
    return sutta_paragraphs
def process_vagga_files(sutta_prefix, output_prefix):
    """
    Process all mula and commentary files for a given sutta prefix
    Updated to handle MN files with multiple suttas per file
    """
    sutta_mapping = {}
    paragraph_mapping = {}
    translation_pairs = []
    
    # Extract nikaya from prefix (s0201 = MN, s0101 = DN)
    nikaya_code = sutta_prefix[1:3]  # '02' for MN, '01' for DN
    
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
                
                # Parse paragraphs
                paragraphs = parse_paragraphs_preserving_structure(xml_content)
                
                # Handle MN vs DN differently
                if nikaya_code == '02':  # MN - multiple suttas per file
                    sutta_titles = extract_mn_sutta_titles(xml_content)
                    sutta_paragraphs = group_paragraphs_by_sutta(paragraphs, sutta_titles)
                    
                    for sutta_name, sutta_paras in sutta_paragraphs.items():
                        for para in sutta_paras:
                            para_num = para['paragraph_number']
                            # Skip sutta title paragraphs
                            if para_num.startswith('sutta_title_'):
                                continue
                                
                            
                            if file_type == 'm':
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
                                    # ~ if pair['sutta'] == sutta_name and pair['paragraph_number'] == para_num:
                                    if  pair['paragraph_number'] == para_num:
                                        pair['commentary_text'] = para['text']
                                        pair['has_commentary'] = True
                                        break
                
                else:  # DN - single sutta per file
                    if file_type == 'm':
                        sutta_name = extract_sutta_name(xml_content)
                        file_key = os.path.basename(xml_file).replace('.xml', '')
                    
                    for para in paragraphs:
                        para_num = para['paragraph_number']
                        
                        if file_type == 'm':
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
    
    # Rest of the function remains the same...
    # Build correct JSON structures
    sutta_data = {}
    para_data = {}
    
    # Build sutta_mapping
    for pair in translation_pairs:
        sutta_name = pair['sutta']
        if sutta_name not in sutta_data:
            sutta_data[sutta_name] = {
                'paragraphs': [],
                'files': [f"{sutta_prefix}*.xml"],
                'paragraph_count': 0
            }
        
        # Only add numeric paragraph numbers (skip sutta_title_*)
        para_num = pair['paragraph_number']
        if para_num.isdigit():  # Only process numeric paragraph numbers
            if para_num not in sutta_data[sutta_name]['paragraphs']:
                sutta_data[sutta_name]['paragraphs'].append(para_num)
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
    
    # Save to separate files
    with open(f"{output_prefix}_sutta_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(sutta_data, f, ensure_ascii=False, indent=2)
    
    with open(f"{output_prefix}_paragraph_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(para_data, f, ensure_ascii=False, indent=2)
    
    with open(f"{output_prefix}_translation_pairs.json", 'w', encoding='utf-8') as f:
        json.dump(translation_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"\n{output_prefix} processing complete!")
    print(f"Total translation pairs: {len(translation_pairs)}")
    print(f"Output files: {output_prefix}_*.json")
        
def main():
    """Process DN2 vagga (s02 series)"""
    # ~ sutta_prefix = "s0101"  # DN2 vagga (DN14-DN23)
    # ~ output_prefix = "dn1_vagga"  # Separate from DN1 files
    sutta_prefix = "s0301"  # DN2 vagga (DN14-DN23)
    output_prefix = "sn1"  # Separate from DN1 files
    
    process_vagga_files(sutta_prefix, output_prefix)

if __name__ == "__main__":
    main()
