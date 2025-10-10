#!/usr/bin/env python3
"""
Hierarchical HTML Generator for Tipitaka
Creates expandable navigation: Nikaya → Vagga → Sutta
"""


import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any

class HierarchicalHTMLGenerator:
    def __init__(self, base_dir: str = ".", output_dir: str = "html_output"):
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create necessary subdirectories
        (self.output_dir / "suttas").mkdir(exist_ok=True)
        (self.output_dir / "styles").mkdir(exist_ok=True)
        
    
    def get_vagga_name(self, nikaya_code: str, vagga_num: str) -> str:
        """Get the Pali name for a vagga"""
        vagga_names = {
            'dn': {
                '1': 'Sīlakkhandhavagga', '2': 'Mahāvagga', '3': 'Pāthikavagga'
            },
            'mn': {
                '1': 'Mūlapariyāyavagga', '2': 'Sīhanādavagga', '3': 'Tatiyavagga'
            }
        }
        
        return vagga_names.get(nikaya_code, {}).get(vagga_num, f"Vagga {vagga_num}")
    
    def extract_sutta_info(self, sutta_name: str):
        """Extract sutta number and clean name"""
        # Handle various sutta name formats
        patterns = [
            r'(\d+)\.\s+(.+)',  # "1. Sutta Name"
            r'(\w+)\s+(\d+)\.?\s*(.+)',  # "DN 1. Sutta Name" 
            r'(.+)\s+(\d+)',  # "Sutta Name 1"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, sutta_name)
            if match:
                if len(match.groups()) == 2:
                    return match.group(1), match.group(2)
                elif len(match.groups()) == 3:
                    return match.group(2), match.group(3)
        
        # If no pattern matches, try to extract number from beginning
        match = re.search(r'^(\d+)', sutta_name)
        if match:
            return match.group(1), sutta_name.replace(match.group(1), '').strip(' .')
        
        return None, sutta_name
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters and clean XML tags"""
        if not text:
            return ""
        
        # First remove XML tags but keep their content
        text = re.sub(r'<[^>]+>', '', text)
        
        # Then escape basic HTML
        text = (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#039;'))
        
        # Convert basic formatting
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        return text.replace('\n', '<br>')
    
    def generate_nikaya_index(self, nikaya_code: str, nikaya_name: str, structure: Dict):
        """Generate index for a specific nikaya - FIXED JavaScript"""
        nikaya_dir = self.output_dir / "nikayas" / nikaya_code
        nikaya_dir.mkdir(parents=True, exist_ok=True)
        
        html = f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nikaya_name} - Tipiṭaka</title>
        <link rel="stylesheet" href="../../styles/main.css">
    </head>
    <body>
        <div class="container">
            <header class="nikaya-header">
                <a href="../../index.html" class="back-link">← Back to Main</a>
                <h1>{nikaya_name}</h1>
            </header>
    
            <div class="vagga-list">
    '''
        
        for vagga_num, vagga_data in sorted(structure['vaggas'].items(), key=lambda x: int(x[0])):
            vagga_name = vagga_data['name']
            
            html += f'''
                <div class="vagga-item">
                    <div class="vagga-header-clickable" onclick="toggleVagga('{nikaya_code}-{vagga_num}')">
                        <h3>{vagga_name} (Vagga {vagga_num})</h3>
                        <span class="expand-icon" id="icon-{nikaya_code}-{vagga_num}">▶</span>
                    </div>
                    <div class="sutta-list" id="{nikaya_code}-{vagga_num}-suttas" style="display: none;">
            '''
            
            suttas = vagga_data.get('suttas', [])
            if not suttas:
                # If no sutta mapping, try to extract from translated texts
                translated_texts = vagga_data.get('translated_texts', [])
                sutta_names = list(set(item.get('sutta', 'Unknown') for item in translated_texts))
                suttas = sorted(sutta_names)
            
            for sutta_name in suttas:
                sutta_num, clean_name = self.extract_sutta_info(sutta_name)
                if sutta_num:
                    clean_filename = re.sub(r'[^\w\s-]', '', clean_name)
                    clean_filename = re.sub(r'[-\s]+', '_', clean_filename).lower()
                    sutta_filename = f"../../suttas/{nikaya_code}{sutta_num}_{clean_filename}.html"
                else:
                    sutta_filename = "#"
                
                html += f'''
                        <a href="{sutta_filename}" class="sutta-link">
                            <span class="sutta-number">{sutta_num if sutta_num else '?'}</span>
                            <span class="sutta-name">{clean_name}</span>
                        </a>
                '''
            
            html += '''
                    </div>
                </div>
            '''
        
        html += '''
            </div>
        </div>
    
        <script>
            function toggleVagga(vaggaId) {
                const suttaList = document.getElementById(vaggaId + '-suttas');
                const icon = document.getElementById('icon-' + vaggaId);
                
                if (suttaList.style.display === 'none') {
                    suttaList.style.display = 'block';
                    icon.textContent = '▼';
                } else {
                    suttaList.style.display = 'none';
                    icon.textContent = '▶';
                }
            }
        </script>
    </body>
    </html>
    '''
        
        with open(nikaya_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def generate_root_index(self, nikayas: Dict):
        """Generate the main index.html - FIXED JavaScript placement"""
        html = f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tipiṭaka Pāli Reader</title>
        <link rel="stylesheet" href="styles/main.css">
    </head>
    <body>
        <div class="container">
            <header class="main-header">
                <h1>Tipiṭaka Pāli Reader</h1>
                <p class="subtitle">Complete Pāli Canon with English Translation</p>
            </header>
    
            <main class="nikaya-container">
                <div class="nikaya-list">
    '''
        
        for nikaya_code, nikaya_name in nikayas.items():
            html += f'''
                    <div class="nikaya-item">
                        <div class="nikaya-header-clickable" onclick="toggleNikaya('{nikaya_code}')">
                            <h2>{nikaya_name}</h2>
                            <span class="expand-icon" id="nikaya-icon-{nikaya_code}">▶</span>
                        </div>
                        <div class="vagga-list" id="nikaya-{nikaya_code}-vaggas" style="display: none;">
                            <div class="loading">Loading vaggas...</div>
                        </div>
                    </div>
            '''
        
        html += '''
                </div>
            </main>
    
            <footer class="main-footer">
                <p>Generated from AI-translated Pāli Tipiṭaka</p>
            </footer>
        </div>
    
        <script>
            async function toggleNikaya(nikayaCode) {
                const vaggaList = document.getElementById('nikaya-' + nikayaCode + '-vaggas');
                const icon = document.getElementById('nikaya-icon-' + nikayaCode);
                
                if (vaggaList.style.display === 'none') {
                    if (vaggaList.innerHTML.includes('Loading')) {
                        try {
                            const response = await fetch(`nikayas/${nikayaCode}/index.html`);
                            const html = await response.text();
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = html;
                            const vaggaContent = tempDiv.querySelector('.vagga-list');
                            
                            if (vaggaContent) {
                                vaggaList.innerHTML = vaggaContent.innerHTML;
                                // ADD THIS: Also add the JavaScript from the fetched page
                                const scripts = tempDiv.querySelectorAll('script');
                                scripts.forEach(script => {
                                    const newScript = document.createElement('script');
                                    newScript.textContent = script.textContent;
                                    document.body.appendChild(newScript);
                                });
                            }
                        } catch (error) {
                            vaggaList.innerHTML = '<div class="error">Failed to load vaggas</div>';
                        }
                    }
                    vaggaList.style.display = 'block';
                    icon.textContent = '▼';
                } else {
                    vaggaList.style.display = 'none';
                    icon.textContent = '▶';
                }
            }
        </script>
    </body>
    </html>
    '''
        
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
   
    def generate_css_styles(self):
        """Generate the CSS stylesheets - COMPLETE VERSION"""
        main_css = '''
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --accent-color: #e74c3c;
        --success-color: #27ae60;
        --bg-color: #f8f9fa;
        --card-bg: #ffffff;
        --text-color: #2c3e50;
        --border-radius: 8px;
        --shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased; 

    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Main Header */
    .main-header {
        text-align: center;
        margin-bottom: 40px;
        padding: 40px 20px;
        background: var(--card-bg);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    
    .main-header h1 {
        color: var(--primary-color);
        margin-bottom: 10px;
        font-size: 2.5em;
    }
    
    .subtitle {
        color: #7f8c8d;
        font-size: 1.2em;
    }
    
    /* Nikaya Header */
    .nikaya-header {
        margin-bottom: 30px;
        padding: 30px;
        background: var(--card-bg);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        text-align: center;
    }
    
    .nikaya-header h1 {
        color: var(--primary-color);
        margin-bottom: 10px;
    }
    
    /* Nikaya List */
    .nikaya-list {
        display: grid;
        gap: 20px;
    }
    
    .nikaya-item {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        overflow: hidden;
    }
    
    .nikaya-header-clickable {
        padding: 20px;
        background: var(--primary-color);
        color: white;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.3s ease;
    }
    
    .nikaya-header-clickable:hover {
        background: #34495e;
    }
    
    .nikaya-header-clickable h2 {
        margin: 0;
        font-size: 1.5em;
    }
    
    .expand-icon {
        font-size: 0.8em;
        transition: transform 0.3s ease;
    }
    
    /* Vagga List */
    .vagga-list {
        padding: 0 20px 20px 20px;
    }
    .vagga-header-clickable {
        padding: 15px;
        background: #f8f9fa;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.3s ease;
    }
    
    .vagga-header-clickable:hover {
        background: #e9ecef;
    }
    .vagga-item {
        margin: 15px 0;
        border: 1px solid #ecf0f1;
        border-radius: var(--border-radius);
        overflow: hidden;
    }
    
    .vagga-header {
        padding: 15px;
        background: #f8f9fa;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.3s ease;
    }
    
    .vagga-header:hover {
        background: #e9ecef;
    }
    
    .vagga-header h3 {
        margin: 0;
        color: var(--primary-color);
    }
    
    /* Sutta List */
    .sutta-list {
        display: grid;
        gap: 10px;
        padding: 15px;
        background: #fafafa;
    }
    
    .sutta-link {
        display: flex;
        padding: 12px 15px;
        background: white;
        border-radius: 4px;
        text-decoration: none;
        color: inherit;
        transition: all 0.3s ease;
        border-left: 3px solid var(--secondary-color);
    }
    
    .sutta-link:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-decoration: none;
        color: inherit;
    }
    
    .sutta-number {
        font-weight: bold;
        color: var(--secondary-color);
        min-width: 60px;
    }
    
    .sutta-name {
        flex: 1;
    }
    
    /* Back links */
    .back-link {
        color: var(--secondary-color);
        text-decoration: none;
        margin-bottom: 10px;
        display: inline-block;
        font-weight: 500;
    }
    
    .back-link:hover {
        text-decoration: underline;
    }
    
    /* Loading and error states */
    .loading, .error {
        padding: 20px;
        text-align: center;
        color: #7f8c8d;
        font-style: italic;
    }
    
    .error {
        color: var(--accent-color);
    }
    
    /* Footer */
    .main-footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        color: #7f8c8d;
        border-top: 1px solid #ecf0f1;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        
        .main-header {
            padding: 20px;
        }
        
        .main-header h1 {
            font-size: 2em;
        }
        
        .nikaya-header {
            padding: 20px;
        }
        
        .nikaya-header-clickable {
            padding: 15px;
        }
        
        .nikaya-header-clickable h2 {
            font-size: 1.3em;
        }
        
        .vagga-header {
            padding: 12px;
        }
        
        .vagga-header h3 {
            font-size: 1.1em;
        }
        
        .sutta-link {
            flex-direction: column;
            gap: 5px;
            padding: 10px;
        }
        
        .sutta-number {
            min-width: auto;
        }
        
        .vagga-list {
            padding: 0 10px 10px 10px;
        }
    }
    
    @media (max-width: 480px) {
        .main-header h1 {
            font-size: 1.8em;
        }
        
        .nikaya-header-clickable h2 {
            font-size: 1.2em;
        }
        
        .vagga-header h3 {
            font-size: 1em;
        }
        
        .sutta-list {
            padding: 10px;
            gap: 8px;
        }
    }
    '''
    
        sutta_css = '''
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --accent-color: #e74c3c;
        --success-color: #27ae60;
        --bg-color: #f8f9fa;
        --card-bg: #ffffff;
        --text-color: #2c3e50;
        --border-radius: 8px;
        --shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
    }
    
    .container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Sutta Header */
    .sutta-header {
        background: var(--card-bg);
        padding: 30px;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin-bottom: 30px;
        text-align: center;
    }
    
    .sutta-header h1 {
        color: var(--primary-color);
        margin-bottom: 10px;
        font-size: 2.2em;
    }
    
    .sutta-meta {
        color: #7f8c8d;
        font-size: 1.1em;
        margin-top: 10px;
    }
    
    /* Back links */
    .back-link {
        color: var(--secondary-color);
        text-decoration: none;
        margin-bottom: 15px;
        display: inline-block;
        font-weight: 500;
        font-size: 0.9em;
    }
    
    .back-link:hover {
        text-decoration: underline;
    }
    
    /* Sutta Content */
    .sutta-content {
        display: grid;
        gap: 20px;
    }



.paragraph-number {
    position: absolute;
    left: 15px;
    top: 25px;
    color: #666;
    font-size: 0.9em;
    font-weight: normal;
}

   
    .paragraph:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    
    .pali-text {
        font-size: 1.3em;
        margin-bottom: 20px;
        color: #2c3e50;
        line-height: 1.8;
        font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
        font-weight: normal;
        text-shadow: 0 0 0.1px currentColor; 
    }
    
    .translation {
        font-size: 1.15em;
        color: #333;
        line-height: 1.7;
        font-family: 'Georgia', serif;
        border-top: 1px solid #ecf0f1;
        padding-top: 15px;
    }
    
    /* Commentary Section */
    .commentary-section {
        background: #f8f9fa;
        padding: 20px;
        margin-top: 20px;
        border-radius: 6px;
        border-left: 3px solid #7f8c8d;
    }
    
    .commentary-pali {
        font-size: 1.2em;
        margin-bottom: 15px;
        color: #2c3e50;
        font-style: italic;
        line-height: 1.8;
        font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
    }
    
    .commentary-english {
        font-size: 1.1em;
        color: #333;
        line-height: 1.6;
        font-family: 'Georgia', serif;
        border-top: 1px solid #ddd;
        padding-top: 10px;
    }
    
    /* Navigation within sutta */
    .sutta-navigation {
        display: flex;
        justify-content: space-between;
        margin: 30px 0;
        padding: 20px;
        background: var(--card-bg);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    
    .nav-btn {
        padding: 12px 24px;
        background: var(--secondary-color);
        color: white;
        text-decoration: none;
        border-radius: 4px;
        transition: all 0.3s ease;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    
    .nav-btn:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        text-decoration: none;
        color: white;
    }
    
    .nav-btn.disabled {
        background: #bdc3c7;
        cursor: not-allowed;
    }
    
    .nav-btn.home {
        background: var(--accent-color);
    }
    
    /* Responsive Design for Sutta Pages */
    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        
        .sutta-header {
            padding: 20px;
        }
        
        .sutta-header h1 {
            font-size: 1.8em;
        }
        
        .paragraph {
            padding: 20px 20px 20px 60px;
        }
        
        .paragraph-number {
            left: 15px;
            top: 20px;
        }
        
        .pali-text {
            font-size: 1.2em;
        }
        
        .translation {
            font-size: 1.1em;
        }
        
        .sutta-navigation {
            flex-direction: column;
            gap: 10px;
            text-align: center;
        }
        
        .nav-btn {
            padding: 10px 20px;
        }
    }
    
    @media (max-width: 480px) {
        .sutta-header h1 {
            font-size: 1.6em;
        }
        
        .paragraph {
            padding: 15px 15px 15px 50px;
        }
        
        .paragraph-number {
            left: 10px;
            top: 15px;
            font-size: 0.8em;
        }
        
        .pali-text {
            font-size: 1.1em;
        }
        
        .translation {
            font-size: 1em;
        }
        
        .commentary-section {
            padding: 15px;
        }
        
        .commentary-pali {
            font-size: 1.1em;
        }
        
        .commentary-english {
            font-size: 1em;
        }
    }
    '''
    
        with open(self.output_dir / "styles" / "main.css", 'w', encoding='utf-8') as f:
            f.write(main_css)
        
        with open(self.output_dir / "styles" / "sutta.css", 'w', encoding='utf-8') as f:
            f.write(sutta_css)
    
    def detect_nikayas(self):
        """Detect which nikayas are available - FIXED"""
        nikayas = {}
        
        # Look for any files with nikaya patterns
        json_files = list(self.base_dir.glob("*translated_texts.json"))
        
        for json_file in json_files:
            # Match patterns like dn1_vagga_translated_texts.json, mn1_translated_texts.json, etc.
            match = re.match(r'([dmsa][n])(\d+)_?(vagga_)?translated_texts\.json', json_file.name)
            if match:
                nikaya_code = match.group(1)
                nikaya_names = {'dn': 'Dīgha Nikāya', 'mn': 'Majjhima Nikāya', 'sn': 'Saṃyutta Nikāya', 'an': 'Aṅguttara Nikāya'}
                if nikaya_code in nikaya_names:
                    nikayas[nikaya_code] = nikaya_names[nikaya_code]
        
        return nikayas
    
    def load_nikaya_structure(self, nikaya_code: str):
        """Load the complete structure for a nikaya - FIXED"""
        structure = {'vaggas': {}}
        
        # Find ALL files for this nikaya
        all_files = list(self.base_dir.glob(f"{nikaya_code}*"))
        
        # Group by vagga number
        vagga_files = {}
        for file_path in all_files:
            # Match patterns like: dn1_vagga_translated_texts.json, mn1_sutta_mapping.json, etc.
            match = re.match(rf"{nikaya_code}(\d+)_(.+)\.json", file_path.name)
            if match:
                vagga_num = match.group(1)
                file_type = match.group(2)
                
                if vagga_num not in vagga_files:
                    vagga_files[vagga_num] = {}
                
                vagga_files[vagga_num][file_type] = file_path
        
        # Process each vagga
        for vagga_num, files in vagga_files.items():
            vagga_structure = {'suttas': [], 'translated_texts': []}
            
            # Load sutta mapping
            if 'sutta_mapping' in files:
                try:
                    with open(files['sutta_mapping'], 'r', encoding='utf-8') as f:
                        vagga_structure['suttas'] = json.load(f)
                except Exception as e:
                    print(f"  Warning: Could not load sutta mapping for {nikaya_code}{vagga_num}: {e}")
            
            # Load translated texts (try multiple possible file patterns)
            # FIX: Use f_path instead of f in the list comprehension
            text_files = [f_path for f_type, f_path in files.items() if 'translated_text' in f_type]
            if text_files:
                try:
                    with open(text_files[0], 'r', encoding='utf-8') as f:
                        vagga_structure['translated_texts'] = json.load(f)
                except Exception as e:
                    print(f"  Warning: Could not load translations for {nikaya_code}{vagga_num}: {e}")
            
            structure['vaggas'][vagga_num] = {
                'suttas': vagga_structure['suttas'],
                'translated_texts': vagga_structure['translated_texts'],
                'name': self.get_vagga_name(nikaya_code, vagga_num)
            }
        
        return structure   
    
    def generate_sutta_page(self, sutta_name: str, paragraphs: List, nikaya_code: str, nikaya_name: str):
        """Generate individual sutta page - FIXED STRUCTURE"""
        sutta_num, clean_name = self.extract_sutta_info(sutta_name)
        
        # Create safe filename
        clean_filename = re.sub(r'[^\w\s-]', '', clean_name)
        clean_filename = re.sub(r'[-\s]+', '_', clean_filename).lower()
        filename = f"{nikaya_code}{sutta_num}_{clean_filename}.html"
        
        # Sort paragraphs by number
        paragraphs = sorted(paragraphs, key=lambda x: int(x.get('paragraph_number', 0)))
        
        html = f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{clean_name} - {nikaya_name}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Gentium+Plus:ital,wght@0,400;0,700;1,400;1,700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Sanskrit&display=swap');

            @media (min-width: 1200px) {{
            .container {{
                max-width: 95%;  /* Use 95% of screen width on large screens */
            }}
        }}
    
            :root {{
                --primary-color: #2c3e50;
                --secondary-color: #3498db;
                --accent-color: #e74c3c;
                --success-color: #27ae60;
                --bg-color: #f8f9fa;
                --card-bg: #ffffff;
                --text-color: #2c3e50;
                --border-radius: 8px;
                --shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
    
            .dark-mode {{
                --bg-color: #1a1a1a;
                --card-bg: #2d2d2d;
                --text-color: #f0f0f0;
                --shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
    
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
    
            body {{
                font-family: 'Times New Roman', serif;
                background: var(--bg-color);
                color: var(--text-color);
                line-height: 1.8;
                transition: all 0.3s ease;
            }}
    
            .container {{
    max-width: 1400px;  /* Increased from 1000px */
    margin: 0 auto;
    padding: 1px;
}}
    
            .sutta-header {{
                background: var(--card-bg);
                padding: 30px;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow);
                margin-bottom: 30px;
                text-align: center;
            }}
    
            .sutta-title {{
                font-size: 2em;
                color: var(--primary-color);
                margin-bottom: 10px;
                font-weight: bold;
            }}
    
            .dark-mode .sutta-title {{
                color: #f0f0f0;
            }}
    
            .sutta-subtitle {{
                color: #7f8c8d;
                font-size: 1.1em;
            }}
    
            .dark-mode .sutta-subtitle {{
                color: #95a5a6;
            }}
    
            .navigation {{
                display: flex;
                justify-content: space-between;
                margin: 30px 0;
                padding: 20px;
                background: var(--card-bg);
                border-radius: var(--border-radius);
                box-shadow: var(--shadow);
            }}
    
            .nav-btn {{
                padding: 10px 20px;
                background: var(--secondary-color);
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: all 0.3s ease;
                font-weight: bold;
            }}
    
            .nav-btn:hover {{
                opacity: 0.9;
                transform: translateY(-1px);
            }}
    
            .nav-btn.disabled {{
                background: #bdc3c7;
                cursor: not-allowed;
            }}
    
            .dark-mode .nav-btn.disabled {{
                background: #555;
            }}
    
            .home-btn {{
                background: var(--accent-color);
            }}
    
            .paragraph {{
    position: relative;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px 20px 20px 50px;
    margin-bottom: 15px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    border-left: 3px solid var(--primary-color);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;  /* Increased gap for better separation */
}}


/* Only add border when commentary is visible */

.paragraph {{
    position: relative;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px 20px 20px 50px;
    margin-bottom: 15px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    border-left: 3px solid var(--primary-color);
    display: block; /* Default: single column as block layout */
    gap: 20px;
}}

.paragraph.with-commentary {{
    display: grid; /* Only use grid when commentary is visible */
    grid-template-columns: 1fr 1fr;
}}

.mula-section {{
    padding-right: 0; /* No border by default */
}}

.paragraph.with-commentary .mula-section {{
    border-right: 1px solid #ecf0f1;
    padding-right: 30px;
}}
commentary-section {{
    background: #f5f5f5;
    padding: 20px;  /* Increased padding */
    border-radius: 6px;
    border-left: 3px solid #7f8c8d;
}}
            .dark-mode .commentary-section {{
                background: #3a3a3a;
                border-left-color: #95a5a6;
            }}
    
            .paragraph-number {{
                position: absolute;
                left: 15px;
                top: 25px;
                color: #666;
                font-size: 0.9em;
                font-weight: normal;
            }}
    
            .dark-mode .paragraph-number {{
                color: #aaa;
            }}
    
            .pali-text {{
                font-size: 1.3em;
                margin-bottom: 20px;
                color: #2c3e50;
                font-weight: normal;
                line-height: 1.8;
                font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
            }}
    
            .devanagari-script .pali-text {{
                font-family: 'Tiro Devanagari Sanskrit', 'Noto Sans Devanagari',
                  text-rendering: optimizeLegibility; 
    font-feature-settings: "kern" 1, "liga" 1, "ccmp" 1; 
     /* Use a very small positive value (e.g., 0.01em to 0.03em). */
    letter-spacing: 0.010em; 
            }}
    
            .dark-mode .pali-text {{
                color: #f0f0f0;
            }}
    
            .translation-text {{
                font-size: 1.25em;
                margin-bottom: 20px;
                color: #222;
                line-height: 1.2;
                font-family: 'Gentium Plus','Heuristica', 'Georgia', serif;
                font-weight: normal;
            }}
    
            .dark-mode .translation-text {{
                color: #e8e8e8;
            }}
    
            .commentary-pali {{
                font-size: 1.2em;
                margin-bottom: 15px;
                color: #2c3e50;
                font-style: italic;
                line-height: 1.8;
                font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
            }}
    
            .devanagari-script .commentary-pali {{
                font-family: 'Tiro Devanagari Sanskrit', 'Noto Sans Devanagari',
                  text-rendering: optimizeLegibility; 
    font-feature-settings: "kern" 1, "liga" 1, "ccmp" 1; 
    /* Use a very small positive value (e.g., 0.01em to 0.03em). */
    letter-spacing: 0.010em; 
     
            }}
    
            .dark-mode .commentary-pali {{
                color: #f0f0f0;
            }}
    
            .commentary-english {{
                font-size: 1.1em;
                color: #333;
                line-height: 1.6;
                font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
                font-weight: normal;
            }}
    
            .dark-mode .commentary-english {{
                color: #e0e0e0;
            }}
    
            .controls {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
    
            .btn {{
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                background: #95a5a6;
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
            }}
    
            .btn:hover {{
                opacity: 0.9;
                transform: translateY(-1px);
            }}
    
            .btn.active {{
                background: var(--success-color);
            }}
    
            .btn.toggle {{
                position: relative;
            }}
    
            .btn.toggle::after {{
                content: "❌";
                margin-left: 8px;
                font-size: 0.9em;
            }}
    
            .btn.toggle.active::after {{
                content: "✅";
            }}
    
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                .sutta-header {{
                    padding: 20px;
                }}
                .sutta-title {{
                    font-size: 1.5em;
                }}
                .navigation {{
                    flex-direction: column;
                    gap: 10px;
                    text-align: center;
                }}
                .paragraph {{
                    padding: 20px 20px 20px 45px;
                    grid-template-columns: 1fr;
                }}
                .mula-section {{
                    border-right: none;
                    padding-right: 0;
                    border-bottom: 1px solid #ecf0f1;
                    padding-bottom: 20px;
                }}
                .paragraph-number {{
                    left: 12px;
                    top: 20px;
                }}
                .controls {{
                    gap: 5px;
                }}
                .btn {{
                    padding: 6px 12px;
                    font-size: 0.9em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="sutta-header">
                <h1 class="sutta-title">{clean_name}</h1>
                <div class="sutta-subtitle">{nikaya_name} {sutta_num}</div>
            </div>
    
            <div class="navigation">
                <a href="../nikayas/{nikaya_code}/index.html" class="nav-btn home-btn">&larr; Back to {nikaya_name}</a>
            </div>
    
            <div class="controls">
                <button class="btn toggle active" onclick="toggleView('mula_pali')">Pali Text</button>
                <button class="btn toggle active" onclick="toggleView('mula_english')">Translation</button>
                <button class="btn toggle" onclick="toggleView('commentary_pali')">Commentary Pali</button>
                <button class="btn toggle" onclick="toggleView('commentary_english')">Commentary English</button>
                <button class="btn toggle active" onclick="toggleScript()">Devanagari Script</button>
                <button class="btn" onclick="toggleTheme()">Dark/Light</button>
            </div>
    
            <div id="content">
    '''
    
        # Add paragraphs
        for item in paragraphs:
            has_commentary = item.get('has_commentary', False) and item.get('commentary_pali')
            
            html += f'''
                <div class="paragraph">
                    <div class="paragraph-number">{item.get('paragraph_number', '')}</div>
                    <div class="mula-section">
                        <div class="pali-text mula-pali-section" data-pali="{self.escape_html(item.get('mula_pali', ''))}">{self.escape_html(item.get('mula_pali', ''))}</div>
                        <div class="translation-text mula-english-section">{self.escape_html(item.get('mula_english', ''))}</div>
                    </div>
                    <div class="commentary-section">
            '''
            
            if has_commentary:
                html += f'''
                        <div class="commentary-pali commentary-pali-section" data-pali="{self.escape_html(item.get('commentary_pali', ''))}">{self.escape_html(item.get('commentary_pali', ''))}</div>
                        <div class="commentary-english commentary-english-section">{self.escape_html(item.get('commentary_english', ''))}</div>
                '''
            else:
                html += f'''
                        <div class="commentary-pali commentary-pali-section" data-pali=""></div>
                        <div class="commentary-english commentary-english-section"></div>
                '''
            
            html += '''
                    </div>
                </div>
            '''
    
        html += f'''
            </div>
    
            <div class="navigation">
                <a href="../nikayas/{nikaya_code}/index.html" class="nav-btn home-btn">&larr; Back to {nikaya_name}</a>
            </div>
        </div>
    
        <script>
            let currentView = {{
            }};
            
            function loadAllSettings() {{
    // Load view settings like dark mode
    const savedViews = localStorage.getItem('paliReaderSettings');
    currentView = savedViews ? JSON.parse(savedViews) : {{
        mula_pali: true,
        mula_english: true,
        commentary_pali: false,
        commentary_english: false,
        devanagari: true
    }};
    updateDisplay();
    }}
            
            // Save settings when changed
            function saveSettings() {{
                localStorage.setItem('paliReaderSettings', JSON.stringify(currentView));
            }}
    
            function toggleView(type) {{
                currentView[type] = !currentView[type];
                
                const buttons = document.querySelectorAll('.btn.toggle');
                buttons.forEach(btn => {{
                    let btnText = btn.textContent.toLowerCase();
                    if ((type === 'mula_english' && btnText.includes('translation')) ||
                        btnText.includes(type.replace('_', ' '))) {{
                        btn.classList.toggle('active', currentView[type]);
                    }}
                }});
                  saveSettings();
                  updateDisplay();
            }}
    
            function toggleScript() {{
                currentView.devanagari = !currentView.devanagari;
                const btn = event.target;
                btn.classList.toggle('active', currentView.devanagari);
                document.body.classList.toggle('devanagari-script', currentView.devanagari);
                updateDisplay();
            }}
    
            function toggleTheme() {{
                document.body.classList.toggle('dark-mode');
                localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
            }}
    
            function convertToDevanagari(text) {{
                if (!text) return text;
                
                text = text.toLowerCase();
                
                const consonants = {{
                    'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ṅ': 'ङ',
                    'c': 'च', 'ch': 'छ', 'j': 'ज', 'jh': 'झ', 'ñ': 'ञ',
                    'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
                    't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
                    'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
                    'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व', 
                    'ś': 'श', 'ṣ': 'ष', 's': 'स', 'h': 'ह'
                }};
                
                const vowelSigns = {{
                    'a': '', 'ā': 'ा', 'i': 'ि', 'ī': 'ी', 'u': 'ु', 'ū': 'ू',
                    'e': 'े', 'o': 'ो'
                }};
                
                const independentVowels = {{
                    'a': 'अ', 'ā': 'आ', 'i': 'इ', 'ī': 'ई', 'u': 'उ', 'ū': 'ऊ',
                    'e': 'ए', 'o': 'ओ'
                }};
                
                let result = '';
                let i = 0;
                
                while (i < text.length) {{
                    const char = text[i];
                    
                    // Handle special characters
                    if (char === 'ṃ' || char === 'ṁ') {{
                        result += 'ं';
                        i++;
                        continue;
                    }}
                    if (char === 'ḥ') {{
                        result += 'ः';
                        i++;
                        continue;
                    }}
                    if (' ,.?!–-""\\'\\'‘’"".'.includes(char)) {{
                        result += char;
                        i++;
                        continue;
                    }}
                    
                    // Check for consonants
                    let consonantFound = null;
                    let consonantLength = 0;
                    
                    // Try 2-character consonants first
                    if (i + 1 < text.length) {{
                        const twoChar = char + text[i + 1];
                        if (consonants[twoChar]) {{
                            consonantFound = consonants[twoChar];
                            consonantLength = 2;
                        }}
                    }}
                    
                    // Try single character consonants
                    if (!consonantFound && consonants[char]) {{
                        consonantFound = consonants[char];
                        consonantLength = 1;
                    }}
                    
                    if (consonantFound) {{
                        const nextIndex = i + consonantLength;
                        
                        // Check what comes after the consonant
                        if (nextIndex < text.length) {{
                            const nextChar = text[nextIndex];
                            
                            // If followed by a vowel sign, use it
                            if (vowelSigns[nextChar] !== undefined) {{
                                result += consonantFound + vowelSigns[nextChar];
                                i += consonantLength + 1;
                            }} 
                            // If followed by another consonant or punctuation, no inherent 'a'
                            else if (consonants[nextChar] || ' ,.?!–-'.includes(nextChar)) {{
                                result += consonantFound + '्';
                                i += consonantLength;
                            }}
                            // Otherwise, assume inherent 'a'
                            else {{
                                result += consonantFound;
                                i += consonantLength;
                            }}
                        }} else {{
                            result += consonantFound;
                            i += consonantLength;
                        }}
                        continue;
                    }}
                    
                    // Check for independent vowels
                    if (independentVowels[char]) {{
                        result += independentVowels[char];
                        i++;
                        continue;
                    }}
                    
                    result += char;
                    i++;
                }}
                
                return result;
            }}
    
            function convertToDevanagariPreservingHTML(text) {{
                const parts = text.split(/(<[^>]*>)/);
                let result = '';
                for (let part of parts) {{
                    if (part.startsWith('<') && part.endsWith('>')) {{
                        result += part;
                    }} else {{
                        result += convertToDevanagari(part);
                    }}
                }}
                return result;
            }}
    
  function updateDisplay() {{
    // Update view toggles
    document.querySelectorAll('.mula-pali-section').forEach(section => {{
        section.style.display = currentView.mula_pali ? 'block' : 'none';
    }});
    document.querySelectorAll('.mula-english-section').forEach(section => {{
        section.style.display = currentView.mula_english ? 'block' : 'none';
    }});
    document.querySelectorAll('.commentary-pali-section').forEach(section => {{
        section.style.display = currentView.commentary_pali ? 'block' : 'none';
    }});
    document.querySelectorAll('.commentary-english-section').forEach(section => {{
        section.style.display = currentView.commentary_english ? 'block' : 'none';
    }});

    // DEBUG: Check what's happening
    console.log('Commentary visibility:', currentView.commentary_pali, currentView.commentary_english);
    
    // FIX: Check if ANY commentary is visible (regardless of content)
    document.querySelectorAll('.paragraph').forEach(paragraph => {{
        const isCommentaryVisible = currentView.commentary_pali || currentView.commentary_english;
        console.log('Setting with-commentary:', isCommentaryVisible);
        paragraph.classList.toggle('with-commentary', isCommentaryVisible);
    }});

    // Update button states
    const paliBtn = document.querySelector('.btn.toggle[onclick="toggleView(\\'mula_pali\\')"]');
    const transBtn = document.querySelector('.btn.toggle[onclick="toggleView(\\'mula_english\\')"]');
    const commPaliBtn = document.querySelector('.btn.toggle[onclick="toggleView(\\'commentary_pali\\')"]');
    const commEngBtn = document.querySelector('.btn.toggle[onclick="toggleView(\\'commentary_english\\')"]');
    
    if (paliBtn) paliBtn.classList.toggle('active', currentView.mula_pali);
    if (transBtn) transBtn.classList.toggle('active', currentView.mula_english);
    if (commPaliBtn) commPaliBtn.classList.toggle('active', currentView.commentary_pali);
    if (commEngBtn) commEngBtn.classList.toggle('active', currentView.commentary_english);

    // Handle Devanagari conversion
    document.querySelectorAll('.pali-text').forEach(element => {{
        const originalText = element.getAttribute('data-pali');
        if (currentView.devanagari) {{
            element.innerHTML = convertToDevanagariPreservingHTML(originalText);
        }} else {{
            element.innerHTML = originalText;
        }}
    }});
    document.querySelectorAll('.commentary-pali').forEach(element => {{
        const originalText = element.getAttribute('data-pali');
        if (currentView.devanagari) {{
            element.innerHTML = convertToDevanagariPreservingHTML(originalText);
        }} else {{
            element.innerHTML = originalText;
        }}
    }});
}}
    
            // Keyboard shortcuts
            document.addEventListener('keydown', function(event) {{
                if (event.ctrlKey) {{
                    if (event.key === 'ArrowRight') {{
                        const paragraphs = document.querySelectorAll('.paragraph');
                        const current = document.elementFromPoint(window.innerWidth/2, window.innerHeight/2);
                        let currentIndex = Array.from(paragraphs).findIndex(p => p.contains(current));
                        if (currentIndex < paragraphs.length - 1) {{
                            paragraphs[currentIndex + 1].scrollIntoView({{ behavior: 'smooth' }});
                        }}
                        event.preventDefault();
                    }} else if (event.key === 'ArrowLeft') {{
                        const paragraphs = document.querySelectorAll('.paragraph');
                        const current = document.elementFromPoint(window.innerWidth/2, window.innerHeight/2);
                        let currentIndex = Array.from(paragraphs).findIndex(p => p.contains(current));
                        if (currentIndex > 0) {{
                            paragraphs[currentIndex - 1].scrollIntoView({{ behavior: 'smooth' }});
                        }}
                        event.preventDefault();
                    }}
                }}
            }});
    
            if (localStorage.getItem('darkMode') === 'true') {{
                document.body.classList.add('dark-mode');
            }}
            
            document.addEventListener('DOMContentLoaded', loadAllSettings);

            
            document.body.classList.toggle('devanagari-script', currentView.devanagari);
            updateDisplay();
        </script>
    </body>
    </html>
    '''
        
        with open(self.output_dir / "suttas" / filename, 'w', encoding='utf-8') as f:
            f.write(html)       
    def generate_all(self):
        """Generate the complete hierarchical HTML system - FIXED"""
        print("Detecting available nikayas...")
        nikayas = self.detect_nikayas()
        print(f"Found: {', '.join(nikayas.values())}")
        
        # Generate CSS
        print("Generating CSS styles...")
        self.generate_css_styles()
        
        # Generate root index
        print("Generating root index.html...")
        self.generate_root_index(nikayas)
        
        # Generate nikaya indexes and sutta pages
        total_suttas = 0
        for nikaya_code, nikaya_name in nikayas.items():
            print(f"Processing {nikaya_name}...")
            
            # Load structure
            structure = self.load_nikaya_structure(nikaya_code)
            vagga_count = len(structure['vaggas'])
            print(f"  Found {vagga_count} vaggas")
            
            # Generate nikaya index
            self.generate_nikaya_index(nikaya_code, nikaya_name, structure)
            print(f"  Generated nikaya index")
            
            # Generate sutta pages
            sutta_count = 0
            for vagga_num, vagga_data in structure['vaggas'].items():
                translated_texts = vagga_data.get('translated_texts', [])
                if translated_texts:
                    # Group paragraphs by sutta
                    sutta_paragraphs = {}
                    for item in translated_texts:
                        sutta_name = item.get('sutta', 'Unknown')
                        if sutta_name not in sutta_paragraphs:
                            sutta_paragraphs[sutta_name] = []
                        sutta_paragraphs[sutta_name].append(item)
                    
                    # Generate sutta pages
                    for sutta_name, paragraphs in sutta_paragraphs.items():
                        self.generate_sutta_page(sutta_name, paragraphs, nikaya_code, nikaya_name)
                        sutta_count += 1
            
            total_suttas += sutta_count
            print(f"  Generated {sutta_count} sutta pages")
        
        print(f"\n✅ Complete! Generated {total_suttas} total sutta pages.")
        print(f"📁 Output directory: {self.output_dir}")
def main():
    """Main function to run the generator"""
    generator = HierarchicalHTMLGenerator()
    generator.generate_all()

if __name__ == "__main__":
    main()
