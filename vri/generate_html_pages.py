#!/usr/bin/env python3
"""
Hierarchical HTML Generator for Tipitaka - Separated Assets Version
Outputs to html/ directory with external CSS/JS files
Preserves user modifications to CSS/JS files
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any

class SeparatedHTMLGenerator:
    def __init__(self, base_dir: str = ".", output_dir: str = "html"):
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create necessary subdirectories
        (self.output_dir / "suttas").mkdir(exist_ok=True)
        (self.output_dir / "nikayas").mkdir(exist_ok=True)
        (self.output_dir / "styles").mkdir(exist_ok=True)
        (self.output_dir / "js").mkdir(exist_ok=True)
    
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
        patterns = [
            r'(\d+)\.\s+(.+)',
            r'(\w+)\s+(\d+)\.?\s*(.+)',
            r'(.+)\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, sutta_name)
            if match:
                if len(match.groups()) == 2:
                    return match.group(1), match.group(2)
                elif len(match.groups()) == 3:
                    return match.group(2), match.group(3)
        
        match = re.search(r'^(\d+)', sutta_name)
        if match:
            return match.group(1), sutta_name.replace(match.group(1), '').strip(' .')
        
        return None, sutta_name
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters and clean XML tags"""
        if not text:
            return ""
        
        text = re.sub(r'<[^>]+>', '', text)
        text = (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#039;'))
        
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        return text.replace('\n', '<br>')
    
    def create_static_assets_if_missing(self):
        """Create CSS and JS files only if they don't exist"""
        # CSS files
        css_files = {
            'main.css': '''/* main.css - Tipitaka Reader Main Styles */
/* This file can be manually modified - script won't overwrite it */

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

.vagga-header h3 {
    margin: 0;
    color: var(--primary-color);
}

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

.loading, .error {
    padding: 20px;
    text-align: center;
    color: #7f8c8d;
    font-style: italic;
}

.error {
    color: var(--accent-color);
}

.main-footer {
    text-align: center;
    margin-top: 40px;
    padding: 20px;
    color: #7f8c8d;
    border-top: 1px solid #ecf0f1;
}

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
''',
            'sutta.css': '''/* sutta.css - Sutta Page Styles */
/* This file can be manually modified - script won't overwrite it */

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

.dark-mode {
    --bg-color: #1a1a1a;
    --card-bg: #2d2d2d;
    --text-color: #f0f0f0;
    --shadow: 0 4px 6px rgba(0,0,0,0.3);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Times New Roman', serif;
    background: var(--bg-color);
    color: var(--text-color);
    line-height: 1.8;
    transition: all 0.3s ease;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1px;
}

.sutta-header {
    background: var(--card-bg);
    padding: 30px;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    margin-bottom: 30px;
    text-align: center;
}

.sutta-title {
    font-size: 2em;
    color: var(--primary-color);
    margin-bottom: 10px;
    font-weight: bold;
}

.dark-mode .sutta-title {
    color: #f0f0f0;
}

.sutta-subtitle {
    color: #7f8c8d;
    font-size: 1.1em;
}

.dark-mode .sutta-subtitle {
    color: #95a5a6;
}

.navigation {
    display: flex;
    justify-content: space-between;
    margin: 30px 0;
    padding: 20px;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}

.nav-btn {
    padding: 10px 20px;
    background: var(--secondary-color);
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: all 0.3s ease;
    font-weight: bold;
}

.nav-btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

.nav-btn.disabled {
    background: #bdc3c7;
    cursor: not-allowed;
}

.dark-mode .nav-btn.disabled {
    background: #555;
}

.home-btn {
    background: var(--accent-color);
}

.paragraph {
    position: relative;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    padding: 20px 20px 20px 50px;
    margin-bottom: 15px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    border-left: 3px solid var(--primary-color);
    display: block;
    gap: 20px;
}

.paragraph.with-commentary {
    display: grid;
    grid-template-columns: 1fr 1fr;
}

.mula-section {
    padding-right: 0;
}

.paragraph.with-commentary .mula-section {
    border-right: 1px solid #ecf0f1;
    padding-right: 30px;
}

.commentary-section {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 6px;
    border-left: 3px solid #7f8c8d;
}

.dark-mode .commentary-section {
    background: #3a3a3a;
    border-left-color: #95a5a6;
}

.paragraph-number {
    position: absolute;
    left: 15px;
    top: 25px;
    color: #666;
    font-size: 0.9em;
    font-weight: normal;
}

.dark-mode .paragraph-number {
    color: #aaa;
}

.pali-text {
    font-size: 1.3em;
    margin-bottom: 20px;
    color: #2c3e50;
    font-weight: normal;
    line-height: 1.8;
    font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
}

.devanagari-script .pali-text {
    font-family: 'Tiro Devanagari Sanskrit', 'Noto Sans Devanagari', serif;
    text-rendering: optimizeLegibility;
    font-feature-settings: "kern" 1, "liga" 1, "ccmp" 1;
    letter-spacing: 0.010em;
}

.dark-mode .pali-text {
    color: #f0f0f0;
}

.translation-text {
    font-size: 1.25em;
    margin-bottom: 20px;
    color: #222;
    line-height: 1.2;
    font-family: 'Gentium Plus','Heuristica', 'Georgia', serif;
    font-weight: normal;
}

.dark-mode .translation-text {
    color: #e8e8e8;
}

.commentary-pali {
    font-size: 1.2em;
    margin-bottom: 15px;
    color: #2c3e50;
    font-style: italic;
    line-height: 1.8;
    font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
}

.devanagari-script .commentary-pali {
    font-family: 'Tiro Devanagari Sanskrit', 'Noto Sans Devanagari', serif;
    text-rendering: optimizeLegibility;
    font-feature-settings: "kern" 1, "liga" 1, "ccmp" 1;
    letter-spacing: 0.010em;
}

.dark-mode .commentary-pali {
    color: #f0f0f0;
}

.commentary-english {
    font-size: 1.1em;
    color: #333;
    line-height: 1.6;
    font-family: 'Gentium Plus', 'Heuristica', 'Georgia', serif;
    font-weight: normal;
}

.dark-mode .commentary-english {
    color: #e0e0e0;
}

.controls {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
    flex-wrap: wrap;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background: #95a5a6;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: bold;
}

.btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

.btn.active {
    background: var(--success-color);
}

.btn.toggle {
    position: relative;
}

.btn.toggle::after {
    content: "❌";
    margin-left: 8px;
    font-size: 0.9em;
}

.btn.toggle.active::after {
    content: "✅";
}

@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    .sutta-header {
        padding: 20px;
    }
    .sutta-title {
        font-size: 1.5em;
    }
    .navigation {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
    .paragraph {
        padding: 20px 20px 20px 45px;
        grid-template-columns: 1fr;
    }
    .mula-section {
        border-right: none;
        padding-right: 0;
        border-bottom: 1px solid #ecf0f1;
        padding-bottom: 20px;
    }
    .paragraph-number {
        left: 12px;
        top: 20px;
    }
    .controls {
        gap: 5px;
    }
    .btn {
        padding: 6px 12px;
        font-size: 0.9em;
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
    .translation-text {
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
        }
        
        # JS files
        js_files = {
            'main.js': '''// main.js - Main page JavaScript
// This file can be manually modified - script won't overwrite it

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
''',
            'sutta.js': '''// sutta.js - Sutta page JavaScript
// This file can be manually modified - script won't overwrite it

let currentView = {};

function loadAllSettings() {
    const savedViews = localStorage.getItem('paliReaderSettings');
    currentView = savedViews ? JSON.parse(savedViews) : {
        mula_pali: true,
        mula_english: true,
        commentary_pali: false,
        commentary_english: false,
        devanagari: true
    };
    updateDisplay();
}

function saveSettings() {
    localStorage.setItem('paliReaderSettings', JSON.stringify(currentView));
}

function toggleView(type) {
    currentView[type] = !currentView[type];
    
    const buttons = document.querySelectorAll('.btn.toggle');
    buttons.forEach(btn => {
        let btnText = btn.textContent.toLowerCase();
        if ((type === 'mula_english' && btnText.includes('translation')) ||
            btnText.includes(type.replace('_', ' '))) {
            btn.classList.toggle('active', currentView[type]);
        }
    });
    saveSettings();
    updateDisplay();
}

function toggleScript() {
    currentView.devanagari = !currentView.devanagari;
    const btn = event.target;
    btn.classList.toggle('active', currentView.devanagari);
    document.body.classList.toggle('devanagari-script', currentView.devanagari);
    updateDisplay();
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

function convertToDevanagari(text) {
    if (!text) return text;
    
    text = text.toLowerCase();
    
    const consonants = {
        'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ṅ': 'ङ',
        'c': 'च', 'ch': 'छ', 'j': 'ज', 'jh': 'झ', 'ñ': 'ञ',
        'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
        't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
        'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
        'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व', 
        'ś': 'श', 'ṣ': 'ष', 's': 'स', 'h': 'ह'
    };
    
    const vowelSigns = {
        'a': '', 'ā': 'ा', 'i': 'ि', 'ī': 'ी', 'u': 'ु', 'ū': 'ू',
        'e': 'े', 'o': 'ो'
    };
    
    const independentVowels = {
        'a': 'अ', 'ā': 'आ', 'i': 'इ', 'ī': 'ई', 'u': 'उ', 'ū': 'ऊ',
        'e': 'ए', 'o': 'ओ'
    };
    
    let result = '';
    let i = 0;
    
    while (i < text.length) {
        const char = text[i];
        
        if (char === 'ṃ' || char === 'ṁ') {
            result += 'ं';
            i++;
            continue;
        }
        if (char === 'ḥ') {
            result += 'ः';
            i++;
            continue;
        }
        if (' ,.?!–-""\\'\\'‘’"".'.includes(char)) {
            result += char;
            i++;
            continue;
        }
        
        let consonantFound = null;
        let consonantLength = 0;
        
        if (i + 1 < text.length) {
            const twoChar = char + text[i + 1];
            if (consonants[twoChar]) {
                consonantFound = consonants[twoChar];
                consonantLength = 2;
            }
        }
        
        if (!consonantFound && consonants[char]) {
            consonantFound = consonants[char];
            consonantLength = 1;
        }
        
        if (consonantFound) {
            const nextIndex = i + consonantLength;
            
            if (nextIndex < text.length) {
                const nextChar = text[nextIndex];
                
                if (vowelSigns[nextChar] !== undefined) {
                    result += consonantFound + vowelSigns[nextChar];
                    i += consonantLength + 1;
                } else if (consonants[nextChar] || ' ,.?!–-'.includes(nextChar)) {
                    result += consonantFound + '्';
                    i += consonantLength;
                } else {
                    result += consonantFound;
                    i += consonantLength;
                }
            } else {
                result += consonantFound;
                i += consonantLength;
            }
            continue;
        }
        
        if (independentVowels[char]) {
            result += independentVowels[char];
            i++;
            continue;
        }
        
        result += char;
        i++;
    }
    
    return result;
}

function convertToDevanagariPreservingHTML(text) {
    const parts = text.split(/(<[^>]*>)/);
    let result = '';
    for (let part of parts) {
        if (part.startsWith('<') && part.endsWith('>')) {
            result += part;
        } else {
            result += convertToDevanagari(part);
        }
    }
    return result;
}

function updateDisplay() {
    document.querySelectorAll('.mula-pali-section').forEach(section => {
        section.style.display = currentView.mula_pali ? 'block' : 'none';
    });
    document.querySelectorAll('.mula-english-section').forEach(section => {
        section.style.display = currentView.mula_english ? 'block' : 'none';
    });
    document.querySelectorAll('.commentary-pali-section').forEach(section => {
        section.style.display = currentView.commentary_pali ? 'block' : 'none';
    });
    document.querySelectorAll('.commentary-english-section').forEach(section => {
        section.style.display = currentView.commentary_english ? 'block' : 'none';
    });

    document.querySelectorAll('.paragraph').forEach(paragraph => {
        const isCommentaryVisible = currentView.commentary_pali || currentView.commentary_english;
        paragraph.classList.toggle('with-commentary', isCommentaryVisible);
    });

    const paliBtn = document.querySelector('.btn.toggle[onclick*="mula_pali"]');
    const transBtn = document.querySelector('.btn.toggle[onclick*="mula_english"]');
    const commPaliBtn = document.querySelector('.btn.toggle[onclick*="commentary_pali"]');
    const commEngBtn = document.querySelector('.btn.toggle[onclick*="commentary_english"]');
    
    if (paliBtn) paliBtn.classList.toggle('active', currentView.mula_pali);
    if (transBtn) transBtn.classList.toggle('active', currentView.mula_english);
    if (commPaliBtn) commPaliBtn.classList.toggle('active', currentView.commentary_pali);
    if (commEngBtn) commEngBtn.classList.toggle('active', currentView.commentary_english);

    document.querySelectorAll('.pali-text').forEach(element => {
        const originalText = element.getAttribute('data-pali');
        if (currentView.devanagari) {
            element.innerHTML = convertToDevanagariPreservingHTML(originalText);
        } else {
            element.innerHTML = originalText;
        }
    });
    document.querySelectorAll('.commentary-pali').forEach(element => {
        const originalText = element.getAttribute('data-pali');
        if (currentView.devanagari) {
            element.innerHTML = convertToDevanagariPreservingHTML(originalText);
        } else {
            element.innerHTML = originalText;
        }
    });
}

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey) {
        if (event.key === 'ArrowRight') {
            const paragraphs = document.querySelectorAll('.paragraph');
            const current = document.elementFromPoint(window.innerWidth/2, window.innerHeight/2);
            let currentIndex = Array.from(paragraphs).findIndex(p => p.contains(current));
            if (currentIndex < paragraphs.length - 1) {
                paragraphs[currentIndex + 1].scrollIntoView({ behavior: 'smooth' });
            }
            event.preventDefault();
        } else if (event.key === 'ArrowLeft') {
            const paragraphs = document.querySelectorAll('.paragraph');
            const current = document.elementFromPoint(window.innerWidth/2, window.innerHeight/2);
            let currentIndex = Array.from(paragraphs).findIndex(p => p.contains(current));
            if (currentIndex > 0) {
                paragraphs[currentIndex - 1].scrollIntoView({ behavior: 'smooth' });
            }
            event.preventDefault();
        }
    }
});

document.addEventListener('DOMContentLoaded', function() {
    loadAllSettings();
    
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
    
    document.body.classList.toggle('devanagari-script', currentView.devanagari);
    updateDisplay();
});
'''
        }
        
        # Create CSS files only if they don't exist
        for css_file, content in css_files.items():
            css_path = self.output_dir / "styles" / css_file
            if not css_path.exists():
                print(f"  Creating {css_file} (will not overwrite if modified)")
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(f"  {css_file} already exists - preserving user modifications")
        
        # Create JS files only if they don't exist
        for js_file, content in js_files.items():
            js_path = self.output_dir / "js" / js_file
            if not js_path.exists():
                print(f"  Creating {js_file} (will not overwrite if modified)")
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(f"  {js_file} already exists - preserving user modifications")
    
    def generate_nikaya_index(self, nikaya_code: str, nikaya_name: str, structure: Dict):
        """Generate index for a specific nikaya using external CSS/JS"""
        nikaya_dir = self.output_dir / "nikayas" / nikaya_code
        nikaya_dir.mkdir(parents=True, exist_ok=True)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nikaya_name} - Tipiṭaka</title>
    <link rel="stylesheet" href="../styles/main.css">
</head>
<body>
    <div class="container">
        <header class="nikaya-header">
            <a href="../index.html" class="back-link">← Back to Main</a>
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
                translated_texts = vagga_data.get('translated_texts', [])
                sutta_names = list(set(item.get('sutta', 'Unknown') for item in translated_texts))
                suttas = sorted(sutta_names)
            
            for sutta_name in suttas:
                sutta_num, clean_name = self.extract_sutta_info(sutta_name)
                if sutta_num:
                    clean_filename = re.sub(r'[^\w\s-]', '', clean_name)
                    clean_filename = re.sub(r'[-\s]+', '_', clean_filename).lower()
                    sutta_filename = f"../suttas/{nikaya_code}{sutta_num}_{clean_filename}.html"
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

    <script src="../js/main.js"></script>
</body>
</html>
'''
        
        with open(nikaya_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def generate_root_index(self, nikayas: Dict):
        """Generate the main index.html using external CSS/JS"""
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

    <script src="js/main.js"></script>
</body>
</html>
'''
        
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def detect_nikayas(self):
        """Detect which nikayas are available"""
        nikayas = {}
        
        json_files = list(self.base_dir.glob("*translated_texts.json"))
        
        for json_file in json_files:
            match = re.match(r'([dmsa][n])(\d+)_?(vagga_)?translated_texts\.json', json_file.name)
            if match:
                nikaya_code = match.group(1)
                nikaya_names = {'dn': 'Dīgha Nikāya', 'mn': 'Majjhima Nikāya', 'sn': 'Saṃyutta Nikāya', 'an': 'Aṅguttara Nikāya'}
                if nikaya_code in nikaya_names:
                    nikayas[nikaya_code] = nikaya_names[nikaya_code]
        
        return nikayas
    
    def load_nikaya_structure(self, nikaya_code: str):
        """Load the complete structure for a nikaya"""
        structure = {'vaggas': {}}
        
        all_files = list(self.base_dir.glob(f"{nikaya_code}*"))
        
        vagga_files = {}
        for file_path in all_files:
            match = re.match(rf"{nikaya_code}(\d+)_(.+)\.json", file_path.name)
            if match:
                vagga_num = match.group(1)
                file_type = match.group(2)
                
                if vagga_num not in vagga_files:
                    vagga_files[vagga_num] = {}
                
                vagga_files[vagga_num][file_type] = file_path
        
        for vagga_num, files in vagga_files.items():
            vagga_structure = {'suttas': [], 'translated_texts': []}
            
            if 'sutta_mapping' in files:
                try:
                    with open(files['sutta_mapping'], 'r', encoding='utf-8') as f:
                        vagga_structure['suttas'] = json.load(f)
                except Exception as e:
                    print(f"  Warning: Could not load sutta mapping for {nikaya_code}{vagga_num}: {e}")
            
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
        """Generate individual sutta page using external CSS/JS"""
        sutta_num, clean_name = self.extract_sutta_info(sutta_name)
        
        clean_filename = re.sub(r'[^\w\s-]', '', clean_name)
        clean_filename = re.sub(r'[-\s]+', '_', clean_filename).lower()
        filename = f"{nikaya_code}{sutta_num}_{clean_filename}.html"
        
        paragraphs = sorted(paragraphs, key=lambda x: int(x.get('paragraph_number', 0)))
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_name} - {nikaya_name}</title>
    <link rel="stylesheet" href="../styles/sutta.css">
    <link href="https://fonts.googleapis.com/css2?family=Gentium+Plus:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Sanskrit&display=swap" rel="stylesheet">
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

    <script src="../js/sutta.js"></script>
</body>
</html>
'''
        
        with open(self.output_dir / "suttas" / filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def generate_all(self):
        """Generate the complete hierarchical HTML system"""
        print("Detecting available nikayas...")
        nikayas = self.detect_nikayas()
        print(f"Found: {', '.join(nikayas.values())}")
        
        # Create static assets (only if missing)
        print("Setting up CSS/JS assets...")
        self.create_static_assets_if_missing()
        
        # Generate root index
        print("Generating root index.html...")
        self.generate_root_index(nikayas)
        
        # Generate nikaya indexes and sutta pages
        total_suttas = 0
        for nikaya_code, nikaya_name in nikayas.items():
            print(f"Processing {nikaya_name}...")
            
            structure = self.load_nikaya_structure(nikaya_code)
            vagga_count = len(structure['vaggas'])
            print(f"  Found {vagga_count} vaggas")
            
            self.generate_nikaya_index(nikaya_code, nikaya_name, structure)
            print(f"  Generated nikaya index")
            
            sutta_count = 0
            for vagga_num, vagga_data in structure['vaggas'].items():
                translated_texts = vagga_data.get('translated_texts', [])
                if translated_texts:
                    sutta_paragraphs = {}
                    for item in translated_texts:
                        sutta_name = item.get('sutta', 'Unknown')
                        if sutta_name not in sutta_paragraphs:
                            sutta_paragraphs[sutta_name] = []
                        sutta_paragraphs[sutta_name].append(item)
                    
                    for sutta_name, paragraphs in sutta_paragraphs.items():
                        self.generate_sutta_page(sutta_name, paragraphs, nikaya_code, nikaya_name)
                        sutta_count += 1
            
            total_suttas += sutta_count
            print(f"  Generated {sutta_count} sutta pages")
        
        print(f"\n✅ Complete! Generated {total_suttas} total sutta pages.")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"💡 Note: CSS/JS files are preserved between runs - modify them freely!")

def main():
    """Main function to run the generator"""
    generator = SeparatedHTMLGenerator()
    generator.generate_all()

if __name__ == "__main__":
    main()
