import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:styled_text/styled_text.dart';
import 'package:tipitaka_pali/data/constants.dart';
import 'package:tipitaka_pali/services/provider/theme_change_notifier.dart';

import '../../../../business_logic/models/search_result.dart';
import '../../../../services/prefs.dart';
import '../../../../services/provider/script_language_provider.dart';
import '../../../../utils/pali_script.dart';
import '../../../../utils/pali_script_converter.dart'; // <--- ADD THIS LINE

class SearchResultListTile extends StatelessWidget {
  final SearchResult result;
  // final String textToHighlight;
  final GestureTapCallback? onTap;

  const SearchResultListTile({super.key, required this.result, this.onTap});
  @override
  Widget build(BuildContext context) {
    // print('text: ${result.description}');
    final bool isDarkMode = context.read<ThemeChangeNotifier>().isDarkMode;
    final script = context.read<ScriptLanguageProvider>().currentScript;
    final double fontSize = script == Script.devanagari ? Prefs.uiFontSize + 2 : Prefs.uiFontSize;

    final style = TextStyle(fontSize: fontSize);
    final styles = {
      highlightTagName: StyledTextTag(
          style: TextStyle(
              fontWeight: isDarkMode ? null : FontWeight.bold,
              fontStyle: isDarkMode ? null : FontStyle.italic,
              color: isDarkMode ? Colors.white : Theme.of(context).primaryColor,
              backgroundColor:
                  isDarkMode ? Theme.of(context).primaryColor : null)),
    };

    final bookName = PaliScript.getScriptOf(
        script: script,
        romanText: result.book.name);
    final pageNumber = PaliScript.getScriptOf(
        script: script,
        romanText: result.pageNumber.toString());

    final bookNameAndPageNumber = bookName;
    final suttaLine = result.suttaName != 'n/a'
        ? '${result.suttaName!}, p. $pageNumber'
        : '(p. $pageNumber)';

    final styelForBookName = TextStyle(
        fontSize: fontSize,
        fontWeight: FontWeight.bold,
        color: Theme.of(context).primaryColor);

    final styleForSuttaName = TextStyle(
      fontWeight: FontWeight.bold,
      fontSize: fontSize,
      color: Theme.of(context).colorScheme.primary,
    );
    return Padding(
      padding: const EdgeInsets.all(4.0),
      child: GestureDetector(
        onTap: onTap,
        child: Card(
          elevation: 8.0,
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // book name and page number
                Text(
                  bookNameAndPageNumber,
                  textAlign: TextAlign.center,
                  style: styelForBookName,
                ),
                Text(
                  suttaLine,
                  style: styleForSuttaName,
                  textAlign: TextAlign.center,
                ),
                Divider(color: Theme.of(context).colorScheme.primary),
                // description text
                StyledText(
                  text: PaliScript.getScriptOf(
                      script: script,
                      romanText: result.description,
                      // <highlight> are used for highlight
                      // text is somehow html
                      isHtmlText: true),
                  // overflow: TextOverflow.ellipsis,
                  // maxLines: 4,
                  style: style,
                  tags: styles,
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}
