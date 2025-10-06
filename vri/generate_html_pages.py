#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Generate multi-page HTML system from translated_texts.json
Generic for DN/MN/SN/AN nikāyas
"""

import json
import os,sys
import re
from pathlib import Path
prefix = sys.argv[1] if len(sys.argv) > 1 else ""
def load_translations():
    """Load the translated texts JSON"""
    with open(f'{prefix}translated_texts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_sutta_info(sutta_name):
    """Extract sutta number and clean name"""
    # ~ print(f"DEBUG: Processing sutta name: '{sutta_name}'")  # Add this line
    
    match = re.match(r'(\d+)\.\s+(.+)', sutta_name)
    if match:
        return match.group(1), match.group(2)
    
    # If no match, try other patterns
    match = re.match(r'(\w+)\s+(\d+)\.?\s*(.+)', sutta_name)
    if match:
        return match.group(2), match.group(3)
    
    # If still no match, return the whole name
    return None, sutta_name
def get_actual_dn_number(vagga_num):
    """Convert vagga number to actual DN number"""
    # First vagga: DN 1-13, Second vagga: DN 14-23, etc.
    dn_mapping = {
        '1': '14', '2': '15', '3': '16', '4': '17', '5': '18', '6': '19',
        '7': '20', '8': '21', '9': '22', '10': '23', '11': '24', '12': '25',
        '13': '26', '14': '27', '15': '28', '16': '29', '17': '30', '18': '31',
        '19': '32', '20': '33', '21': '34'
    }
    return dn_mapping.get(vagga_num, vagga_num)
    
def detect_nikaya(suttas):
    """Detect which nikāya this is based on sutta names"""
    first_sutta = next(iter(suttas.keys()))
    # ~ print(f"DEBUG: First sutta: '{first_sutta}'")  # Add this to see what we're checking
    
    if 'Brahmajālasutta' in first_sutta:
        return 'dn', 'Dīgha Nikāya'
    elif 'Mūlapariyāyasutta' in first_sutta:
        return 'mn', 'Majjhima Nikāya' 
    elif 'Oghataraṇasutta' in first_sutta:
        return 'sn', 'Saṃyutta Nikāya'
    elif 'Cittapariyādānasutta' in first_sutta:
        return 'an', 'Aṅguttara Nikāya'
    else:
        # Try to detect from sutta numbers or patterns
        if any('Mahā' in name for name in suttas.keys()):
            return 'dn', 'Dīgha Nikāya'  # Long suttas with "Mahā" prefix are usually DN
        else:
            return 'dn', 'Dīgha Nikāya'  # Default to DN since you have Mahā suttas
            
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
    """Escape HTML special characters but preserve formatting"""
    if not text:
        return ""
    
    # First escape all HTML
    text = (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#039;'))
    
    # Then unescape allowed HTML tags
    allowed_tags = ['i', 'b', 'em', 'strong', 'br', 'p']
    for tag in allowed_tags:
        text = text.replace(f'&lt;{tag}&gt;', f'<{tag}>')
        text = text.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    
    # Convert XML <p> tags to HTML paragraph breaks
    text = re.sub(r'&lt;p[^&]*&gt;', '<br><br>', text)
    text = text.replace('&lt;/p&gt;', '')
    
    # Convert Markdown * to HTML <i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    return text.replace('\n', '<br>')

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
         @import url('https://fonts.googleapis.com/css2?family=Gentium+Plus:ital,wght@0,400;0,700;1,400;1,700&display=swap');

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
            max-width: 1000px;
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
            padding: 20px 20px 20px 50px;  /* Reduced padding */
            margin-bottom: 15px;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            border-left: 3px solid var(--primary-color);
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
        
        @font-face {{
            font-family: 'Tiro Devanagari Hindi';
            src: url('../../assets/fonts/TiroDevanagariHindi-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}

        .pali-text {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #2c3e50;
            font-weight: bold;
            line-height: 1.8;
            font-family: 'Times New Roman', 'Gentium Plus', serif; /* Roman font */

        }}
        
        .devanagari-script .pali-text {{
            font-family: 'Tiro Devanagari Hindi', sans-serif; /* Devanagari font */
        }}


        .dark-mode .pali-text {{
            color: #f0f0f0;
        }}

        .translation-text {{
            font-size: 1.25em;
            margin-bottom: 20px;
            color: #222;
            line-height: 1.2;
            font-family: 'Gentium Plus','Heuristica',  'Georgia', serif;
            font-weight: normal;
        }}
        
        

        .dark-mode .translation-text {{
            color: #e8e8e8;
        }}

        .commentary-section {{
            background: #f5f5f5;
            padding: 10px;
            margin-top: 20px;
            border-radius: 6px;
            border-left: 3px solid #7f8c8d;
        }}

        .dark-mode .commentary-section {{
            background: #3a3a3a;
            border-left-color: #95a5a6;
        }}

        .commentary-pali {{
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #2c3e50;
            font-style: italic;
            line-height: 1.8;
            font-family: 'Times New Roman', 'Gentium Plus', serif; /* Roman font */
        }}
        
        .devanagari-script .commentary-pali {{
            font-family: 'Tiro Devanagari Hindi', 'Noto Sans Devanagari', sans-serif; /* Devanagari font */
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
            
            .paragraph {{
                padding: 20px 20px 20px 45px;
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
            {'<a href="' + get_sutta_filename(prev_sutta, nikaya_code) + '" class="nav-btn">← Previous: ' + extract_sutta_info(prev_sutta)[1] + '</a>' if prev_sutta else '<span class="nav-btn disabled">← Previous</span>'}
            <a href="index.html" class="nav-btn home-btn">Home</a>
            {'<a href="' + get_sutta_filename(next_sutta, nikaya_code) + '" class="nav-btn">Next: ' + extract_sutta_info(next_sutta)[1] + ' →</a>' if next_sutta else '<span class="nav-btn disabled">Next →</span>'}
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
        has_commentary = item['has_commentary'] and item['commentary_pali']
        
        html += f'''
            <div class="paragraph">
                <div class="paragraph-number">{item['paragraph_number']}</div>
                
                <div class="pali-text mula-pali-section" data-pali="{escape_html(item['mula_pali'])}">{escape_html(item['mula_pali'])}</div>
                
                <div class="translation-text mula-english-section">{escape_html(item['mula_english'])}</div>
        '''

        if has_commentary:
            html += f'''
                <div class="commentary-section">
                    <div class="commentary-pali commentary-pali-section" data-pali="{escape_html(item['commentary_pali'])}">{escape_html(item['commentary_pali'])}</div>
                    <div class="commentary-english commentary-english-section">{escape_html(item['commentary_english'])}</div>
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
            commentary_pali: false,
            commentary_english: false,
            devanagari: true
        }};
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
            updateDisplay();
        }}

        function toggleCommentary() {{
            currentView.show_commentary = !currentView.show_commentary;
            const btn = event.target;
            btn.classList.toggle('active', currentView.show_commentary);
            document.body.classList.toggle('show-commentary', currentView.show_commentary);
            localStorage.setItem('showCommentary', currentView.show_commentary);
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
                            result += consonantFound + '्'; // Add virama for doubled consonants
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


        function convertToDevanagariPreservingHTML(text) {{
            // Split text into HTML tags and content
            const parts = text.split(/(<[^>]*>)/);
            
            let result = '';
            for (let part of parts) {{
                if (part.startsWith('<') && part.endsWith('>')) {{
                    // This is an HTML tag, keep it as-is
                    result += part;
                }} else {{
                    // This is text content, convert to Devanagari
                    result += convertToDevanagari(part);
                }}
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
        
        

        // Load saved settings
        if (localStorage.getItem('darkMode') === 'true') {{
            document.body.classList.add('dark-mode');
        }}
        
         // Set initial script state
        document.body.classList.toggle('devanagari-script', currentView.devanagari);

        // Initial display update
        updateDisplay();
        
        const savedCommentary = localStorage.getItem('showCommentary');
        if (savedCommentary !== null) {{
            currentView.show_commentary = savedCommentary === 'true';
            document.body.classList.toggle('show-commentary', currentView.show_commentary);
            // Find and update the commentary button state
            const buttons = document.querySelectorAll('.btn.toggle');
            buttons.forEach(btn => {{
                if (btn.textContent.includes('Commentary')) {{
                    btn.classList.toggle('active', currentView.show_commentary);
                }}
            }});
        }}

        // Initial display update
        updateDisplay();
        
                // Keyboard shortcuts
        document.addEventListener('keydown', function(event) {{
            if (event.ctrlKey) {{
                if (event.key === 'ArrowRight') {{
                    // Next paragraph
                    const paragraphs = document.querySelectorAll('.paragraph');
                    const current = document.elementFromPoint(window.innerWidth/2, window.innerHeight/2);
                    let currentIndex = Array.from(paragraphs).findIndex(p => p.contains(current));
                    if (currentIndex < paragraphs.length - 1) {{
                        paragraphs[currentIndex + 1].scrollIntoView({{ behavior: 'smooth' }});
                    }}
                    event.preventDefault();
                }} else if (event.key === 'ArrowLeft') {{
                    // Previous paragraph  
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
    <link href="https://fonts.googleapis.com/css2?family=Gentium+Plus:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">

    <style>
            @import url('https://fonts.googleapis.com/css2?family=Gentium+Plus:ital,wght@0,400;0,700;1,400;1,700&display=swap');

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
            padding: 10px;  /* Reduced from 20px */

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
        
        # For DN, use actual DN numbers instead of vagga numbers
        if nikaya_code == 'dn' and sutta_num:
            actual_num = get_actual_dn_number(sutta_num)
        else:
            actual_num = sutta_num
            
        html += f'''
            <a href="{filename}" class="sutta-item">
                <div class="sutta-number">{nikaya_code.upper()} {actual_num if actual_num else "?"}</div>
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
