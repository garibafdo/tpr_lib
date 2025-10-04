import os
import xml.etree.ElementTree as ET

def xml_to_html(xml_file):
    """Convert a single XML file to HTML"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        html_file = xml_file.replace('.xml', '.html')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>''' + xml_file + '''</title>
    <style>
        body {
            font-family: "Times New Roman", serif;
            margin: 40px;
            line-height: 1.6;
            font-size: 16px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .para {
            margin: 15px 0;
            text-align: justify;
        }
        .num {
            color: #888;
            font-weight: bold;
            margin-right: 15px;
            font-family: monospace;
            display: inline-block;
            min-width: 60px;
        }
    </style>
</head>
<body>
    <h1>''' + xml_file + '''</h1>
''')
            
            for p in root.findall('.//p'):
                para_num = p.get('n', '')
                text = ''.join(p.itertext()).strip()
                if text:
                    f.write(f'    <div class="para"><span class="num">{para_num}</span>{text}</div>\n')
            
            f.write('</body>\n</html>')
        
        print(f"Created: {html_file}")
        
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")

# Convert all XML files
for filename in os.listdir('.'):
    if filename.endswith('.xml'):
        xml_to_html(filename)

print("Done! Open any .html file in your browser.")
