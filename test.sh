#!/bin/bash

DB_PATH="/home/ani/.local/share/com.paauk.tipitaka_pali_reader/tipitaka_pali.db"

echo "=== PARAGRAPH-TO-PARAGRAPH MAPPING ANALYSIS ==="
echo ""

# First, let's see the paragraph structure for DN2 Sāmaññaphala
echo "📖 PARAGRAPHS IN DN2 SĀMAÑÑAPHALA (mula_di_01):"
sqlite3 -header -column "$DB_PATH" "SELECT p.paragraph_number, p.page_number, substr(pa.content, 1, 80) as content_preview 
FROM paragraphs p 
JOIN pages pa ON p.book_id = pa.bookid AND p.page_number = pa.page 
WHERE p.book_id = 'mula_di_01' 
AND p.page_number BETWEEN 44 AND 60
ORDER BY p.paragraph_number
LIMIT 20;"
echo ""

# Now let's see the exact mapping for these paragraphs
echo "🔗 PARAGRAPH MAPPING FOR DN2 SĀMAÑÑAPHALA:"
sqlite3 -header -column "$DB_PATH" "SELECT pm.paragraph as mula_para, 
       pm.base_page_number as mula_page, 
       pm.exp_book_id as commentary_book,
       pm.exp_page_number as commentary_page,
       substr(mula.content, 1, 60) as mula_preview,
       substr(comm.content, 1, 60) as commentary_preview
FROM paragraph_mapping pm
LEFT JOIN pages mula ON mula.bookid = 'mula_di_01' AND mula.page = pm.base_page_number
LEFT JOIN pages comm ON comm.bookid = pm.exp_book_id AND comm.page = pm.exp_page_number
WHERE pm.base_book_id = 'mula_di_01' 
AND pm.base_page_number BETWEEN 44 AND 60
ORDER BY pm.paragraph
LIMIT 25;"
echo ""

# Let's also check if there are multiple commentary paragraphs per sutta paragraph
echo "📊 MAPPING DENSITY ANALYSIS:"
sqlite3 -header -column "$DB_PATH" "SELECT base_page_number as mula_page, 
       COUNT(*) as commentary_paragraphs,
       GROUP_CONCAT(DISTINCT exp_page_number) as commentary_pages
FROM paragraph_mapping 
WHERE base_book_id = 'mula_di_01' 
AND base_page_number BETWEEN 44 AND 60
GROUP BY base_page_number
ORDER BY base_page_number;"
echo ""

# Check the actual paragraph numbers in the mapping vs paragraphs table
echo "🔢 PARAGRAPH NUMBER ANALYSIS:"
sqlite3 -header -column "$DB_PATH" "SELECT 'paragraphs_table' as source, MIN(paragraph_number) as min_para, MAX(paragraph_number) as max_para, COUNT(*) as total
FROM paragraphs WHERE book_id = 'mula_di_01' AND page_number BETWEEN 44 AND 60
UNION ALL
SELECT 'mapping_table' as source, MIN(paragraph) as min_para, MAX(paragraph) as max_para, COUNT(*) as total
FROM paragraph_mapping WHERE base_book_id = 'mula_di_01' AND base_page_number BETWEEN 44 AND 60;"
echo ""

# Let's see a specific example - first few paragraphs of DN2
echo "🎯 SPECIFIC EXAMPLE - FIRST 5 PARAGRAPHS OF DN2:"
sqlite3 -header -column "$DB_PATH" "SELECT pm.paragraph as mula_para_num,
       pm.base_page_number as mula_page,
       pm.exp_page_number as commentary_page,
       (SELECT paragraph_number FROM paragraphs WHERE book_id = 'mula_di_01' AND page_number = pm.base_page_number LIMIT 1) as para_table_num,
       substr((SELECT content FROM pages WHERE bookid = 'mula_di_01' AND page = pm.base_page_number), 1, 70) as mula_content,
       substr((SELECT content FROM pages WHERE bookid = 'attha_di_01' AND page = pm.exp_page_number), 1, 70) as commentary_content
FROM paragraph_mapping pm
WHERE pm.base_book_id = 'mula_di_01' 
AND pm.base_page_number BETWEEN 44 AND 60
ORDER BY pm.paragraph
LIMIT 5;"
echo ""

# Check if paragraph numbers are sequential or have gaps
echo "📈 PARAGRAPH SEQUENCE ANALYSIS:"
sqlite3 -header -column "$DB_PATH" "WITH para_sequence AS (
  SELECT paragraph, 
         paragraph - LAG(paragraph) OVER (ORDER BY paragraph) as gap
  FROM paragraph_mapping 
  WHERE base_book_id = 'mula_di_01' 
  AND base_page_number BETWEEN 44 AND 60
)
SELECT MIN(paragraph) as first_para, 
       MAX(paragraph) as last_para,
       COUNT(*) as total_paras,
       COUNT(CASE WHEN gap > 1 THEN 1 END) as gaps_count,
       GROUP_CONCAT(CASE WHEN gap > 1 THEN gap || ' at para ' || (paragraph - gap) ELSE NULL END) as gap_locations
FROM para_sequence;"
echo ""

# Final mapping summary for the Python script
echo "🎯 FINAL MAPPING FOR PYTHON SCRIPT:"
sqlite3 -header -column "$DB_PATH" "SELECT 
  'For mula_di_01 page ' || pm.base_page_number || ' (para ' || pm.paragraph || ')' as sutta_location,
  '-> commentary at attha_di_01 page ' || pm.exp_page_number as commentary_location,
  substr((SELECT content FROM pages WHERE bookid = 'mula_di_01' AND page = pm.base_page_number), 1, 50) as mula_snippet
FROM paragraph_mapping pm
WHERE pm.base_book_id = 'mula_di_01' 
AND pm.base_page_number BETWEEN 44 AND 60
ORDER BY pm.paragraph
LIMIT 10;"
