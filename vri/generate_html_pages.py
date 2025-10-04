#!/usr/bin/env python3
"""
Generate multi-page HTML system from translated_texts.json
Generic for DN/MN/SN/AN nikāyas
"""

import json
import os
import re
from pathlib import Path

def load_translations():
    """Load the translated texts JSON"""
    with open('translated_texts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_sutta_info(sutta_name):
    """Extract sutta number and clean name"""
    match = re.match(r'(\d+)\.\s+(.+)', sutta_name)
    if match:
        return match.group(1), match.group(2)
    return None, sutta_name

def detect_nikaya(suttas):
    """Detect which nikāya this is based on sutta names"""
    first_sutta = next(iter(suttas.keys()))
    if 'Brahmajālasutta' in first_sutta:
        return 'dn', 'Dīgha Nikāya'
    elif 'Mūlapariyāyasutta' in first_sutta:
        return 'mn', 'Majjhima Nikāya' 
    elif 'Oghataraṇasutta' in first_sutta:
        return 'sn', 'Saṃyutta Nikāya'
    elif 'Cittapariyādānasutta' in first_sutta:
        return 'an', 'Aṅguttara Nikāya'
    else:
        return 'unknown', 'Tipiṭaka'

def group_by_sutta(translations):
    """Group paragraphs by sutta"""
    suttas = {}
    for item in translations:
        sutta_name = item['sutta']
        if sutta_name not in suttas:
            suttas[sutta_name] = []
        suttas[sutta_name].append(item)
    
    # Sort paragraphs within each sutta
    for sutta_name, paragraphs in suttas.items():
        suttas[sutta_name] = sorted(paragraphs, key=lambda x: int(x['paragraph_number']))
    
    return suttas

def get_sutta_filename(sutta_name, nikaya_code):
    """Convert sutta name to filename"""
    if not sutta_name:
        return "#"
    sutta_num, clean_name = extract_sutta_info(sutta_name)
    clean_filename = re.sub(r'[^\w\s-]', '', clean_name)
    clean_filename = re.sub(r'[-\s]+', '_', clean_filename)
    return f"suttas/{nikaya_code}{sutta_num}_{clean_filename.lower()}.html"

def escape_html(text):
    """Escape HTML special characters"""
    if not text:
        return ""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#039;')
                .replace('\n', '<br>'))

def generate_sutta_html(sutta_name, paragraphs, all_suttas, nikaya_code, nikaya_name):
    """Generate individual sutta HTML page"""
    sutta_num, clean_name = extract_sutta_info(sutta_name)
    
    # Get previous and next sutta for navigation
    sutta_list = sorted(all_suttas.keys())
    current_index = sutta_list.index(sutta_name)
    prev_sutta = sutta_list[current_index - 1] if current_index > 0 else None
    next_sutta = sutta_list[current_index + 1] if current_index < len(sutta_list) - 1 else None
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{sutta_name} - Tipiṭaka Translations</title>
    <style>
        /* Base styles */
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
            --text-color: #e0e0e0;
            --shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
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
        }}

        .sutta-subtitle {{
            color: #7f8c8d;
            font-size: 1.1em;
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
        }}

        .nav-btn:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}

        .nav-btn.disabled {{
            background: #bdc3c7;
            cursor: not-allowed;
        }}

        .home-btn {{
            background: var(--accent-color);
        }}

        .paragraph {{
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }}

        .paragraph-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--secondary-color);
        }}

        .para-number {{
            background: var(--primary-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }}

        .section {{
            margin: 25px 0;
        }}

        .section-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--primary-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-title::before {{
            content: "•";
            color: var(--accent-color);
            font-size: 1.5em;
        }}

        .text-content {{
            background: var(--bg-color);
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid var(--accent-color);
            margin: 10px 0;
            transition: all 0.3s ease;
        }}

        .pali-text {{
            border-left-color: #e74c3c;
            font-size: 1.2em;
            line-height: 1.8;
        }}

        .english-text {{
            border-left-color: #3498db;
        }}

        .commentary-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }}

        .commentary-section .section-title {{
            color: white;
        }}

        .commentary-section .section-title::before {{
            color: #f1c40f;
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
            background: var(--secondary-color);
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .btn:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}

        .btn.active {{
            background: var(--success-color);
        }}

        .btn.toggle {{
            background: #95a5a6;
            position: relative;
        }}

        .btn.toggle.active {{
            background: var(--success-color);
        }}

        .btn.toggle::after {{
            content: "❌";
            margin-left: 8px;
            font-size: 0.9em;
        }}

        .btn.toggle.active::after {{
            content: "✅";
        }}

        .hidden {{
            display: none;
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
            {'<a href="' + get_sutta_filename(prev_sutta, nikaya_code) + '" class="nav-btn">← Previous: ' + extract_sutta_info(prev_sutta)[1] + '</a>' if prev_sutta else '<span class="nav-btn disabled">← Previous</span>'}
            <a href="index.html" class="nav-btn home-btn">Home</a>
            {'<a href="' + get_sutta_filename(next_sutta, nikaya_code) + '" class="nav-btn">Next: ' + extract_sutta_info(next_sutta)[1] + ' →</a>' if next_sutta else '<span class="nav-btn disabled">Next →</span>'}
        </div>

        <div class="controls">
            <button class="btn toggle active" onclick="toggleView('mula_pali')">Mula Pali</button>
            <button class="btn toggle active" onclick="toggleView('mula_english')">Mula English</button>
            <button class="btn toggle active" onclick="toggleView('commentary_pali')">Commentary Pali</button>
            <button class="btn toggle active" onclick="toggleView('commentary_english')">Commentary English</button>
            <button class="btn toggle" onclick="toggleScript()">Devanagari Script</button>
            <button class="btn" onclick="toggleTheme()">Dark/Light</button>
        </div>

        <div id="content">
'''

    # Add paragraphs
    for item in paragraphs:
        has_commentary = item['has_commentary'] and item['commentary_pali']
        
        html += f'''
            <div class="paragraph">
                <div class="paragraph-header">
                    <div class="para-number">Paragraph {item['paragraph_number']}</div>
                </div>

                <div class="section mula-pali-section">
                    <div class="section-title">Mūla (Source Text)</div>
                    <div class="text-content pali-text" data-pali="{escape_html(item['mula_pali'])}">{escape_html(item['mula_pali'])}</div>
                </div>

                <div class="section mula-english-section">
                    <div class="section-title">English Translation</div>
                    <div class="text-content english-text">{escape_html(item['mula_english'])}</div>
                </div>
'''

        if has_commentary:
            html += f'''
                <div class="commentary-section">
                    <div class="section-title">Aṭṭhakathā (Commentary)</div>
                    
                    <div class="section commentary-pali-section">
                        <div class="section-title">Pali Commentary</div>
                        <div class="text-content pali-text" data-pali="{escape_html(item['commentary_pali'])}">{escape_html(item['commentary_pali'])}</div>
                    </div>

                    <div class="section commentary-english-section">
                        <div class="section-title">English Commentary</div>
                        <div class="text-content english-text">{escape_html(item['commentary_english'])}</div>
                    </div>
                </div>
            '''
        else:
            html += '''
                <div style="text-align: center; color: #7f8c8d; font-style: italic; padding: 10px;">
                    No commentary available for this paragraph
                </div>
            '''

        html += '</div>'

    html += f'''
        </div>

        <div class="navigation">
            {'<a href="' + get_sutta_filename(prev_sutta, nikaya_code) + '" class="nav-btn">← Previous: ' + extract_sutta_info(prev_sutta)[1] + '</a>' if prev_sutta else '<span class="nav-btn disabled">← Previous</span>'}
            <a href="index.html" class="nav-btn home-btn">Home</a>
            {'<a href="' + get_sutta_filename(next_sutta, nikaya_code) + '" class="nav-btn">Next: ' + extract_sutta_info(next_sutta)[1] + ' →</a>' if next_sutta else '<span class="nav-btn disabled">Next →</span>'}
        </div>
    </div>

    <script>
        let currentView = {{
            mula_pali: true,
            mula_english: true,
            commentary_pali: true,
            commentary_english: true,
            devanagari: false
        }};

        function toggleView(type) {{
            currentView[type] = !currentView[type];
            const buttons = document.querySelectorAll('.btn.toggle');
            buttons.forEach(btn => {{
                if (btn.textContent.toLowerCase().includes(type.replace('_', ' '))) {{
                    btn.classList.toggle('active', currentView[type]);
                }}
            }});
            updateDisplay();
        }}

        function toggleScript() {{
            currentView.devanagari = !currentView.devanagari;
            const btn = event.target;
            btn.classList.toggle('active', currentView.devanagari);
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
                            result += consonantFound;
                            i += consonantLength;
                        }}
                        // Otherwise, assume inherent 'a'
                        else {{
                            result += consonantFound;
                            i += consonantLength;
                        }}
                    }} else {{
                        // End of text - no inherent 'a'
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
                
                // Keep anything else as-is
                result += char;
                i++;
            }}
            
            return result;
        }}

        function updateDisplay() {{
            // Handle view toggles
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

            // Handle Devanagari conversion
            document.querySelectorAll('.pali-text').forEach(element => {{
                const originalText = element.getAttribute('data-pali');
                if (currentView.devanagari) {{
                    element.innerHTML = convertToDevanagari(originalText);
                }} else {{
                    element.innerHTML = originalText;
                }}
            }});
        }}

        // Load saved theme
        if (localStorage.getItem('darkMode') === 'true') {{
            document.body.classList.add('dark-mode');
        }}

        // Initial display update
        updateDisplay();
    </script>
</body>
</html>
'''

    return html

def generate_index_html(suttas, nikaya_code, nikaya_name):
    """Generate the main index page"""
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tipiṭaka Translations - {nikaya_name}</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #2c3e50;
            --border-radius: 8px;
            --shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 20px;
            background: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }}

        h1 {{
            color: var(--primary-color);
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}

        .sutta-list {{
            display: grid;
            gap: 15px;
        }}

        .sutta-item {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: block;
        }}

        .sutta-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}

        .sutta-number {{
            font-weight: bold;
            color: var(--secondary-color);
            margin-bottom: 5px;
        }}

        .sutta-name {{
            font-size: 1.1em;
            margin-bottom: 5px;
        }}

        .sutta-stats {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tipiṭaka Translations</h1>
            <div class="subtitle">{nikaya_name}</div>
        </div>

        <div class="sutta-list">
'''

    # Add sutta links
    for sutta_name in sorted(suttas.keys()):
        paragraphs = suttas[sutta_name]
        sutta_num, clean_name = extract_sutta_info(sutta_name)
        filename = get_sutta_filename(sutta_name, nikaya_code)
        
        # Count paragraphs with commentary
        with_commentary = sum(1 for p in paragraphs if p['has_commentary'])
        
        html += f'''
            <a href="{filename}" class="sutta-item">
                <div class="sutta-number">{nikaya_code.upper()} {sutta_num}</div>
                <div class="sutta-name">{clean_name}</div>
                <div class="sutta-stats">{len(paragraphs)} paragraphs • {with_commentary} with commentary</div>
            </a>
'''

    html += f'''
        </div>

        <div class="footer">
            <p>Generated from complete {nikaya_name} translation</p>
        </div>
    </div>
</body>
</html>
'''
    return html

def main():
    """Generate the multi-page HTML system"""
    print("Loading translations...")
    translations = load_translations()
    
    print("Grouping by sutta...")
    suttas = group_by_sutta(translations)
    
    # Detect nikāya
    nikaya_code, nikaya_name = detect_nikaya(suttas)
    print(f"Detected: {nikaya_name} ({nikaya_code})")
    
    # Create suttas directory
    os.makedirs('suttas', exist_ok=True)
    
    print(f"Generating HTML for {len(suttas)} suttas...")
    
    # Generate individual sutta pages
    for sutta_name, paragraphs in suttas.items():
        filename = get_sutta_filename(sutta_name, nikaya_code)
        html = generate_sutta_html(sutta_name, paragraphs, suttas, nikaya_code, nikaya_name)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  Generated: {filename}")
    
    # Generate index page
    print("Generating index.html...")
    index_html = generate_index_html(suttas, nikaya_code, nikaya_name)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print("Done! Multi-page HTML system generated.")
    print(f" - index.html (main navigation)")
    print(f" - suttas/ ({len(suttas)} individual sutta pages)")
    print(f" - {nikaya_name} complete")

if __name__ == "__main__":
    main()
