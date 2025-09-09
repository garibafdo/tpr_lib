import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tipitaka_pali/ui/widgets/colored_text.dart';
import 'package:tipitaka_pali/utils/font_utils.dart';

import '../../services/prefs.dart';
import '../../services/provider/script_language_provider.dart';
import '../../utils/pali_script.dart';
import 'book.dart';
import 'category.dart';

abstract class ListItem {
  Widget build(BuildContext context);
}

/// A ListItem that contains data to display a heading.
class CategoryItem implements ListItem {
  final Category category;

  CategoryItem(this.category);

  @override
  Widget build(BuildContext context) {
    return ColoredText(
      PaliScript.getScriptOf(
          script: context.read<ScriptLanguageProvider>().currentScript,
          romanText: category.name),
      style: TextStyle(
          fontSize: Prefs.uiFontSize + 4,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
          fontFamily: FontUtils.getfontName(
              script: context.read<ScriptLanguageProvider>().currentScript)),
    );
  }
}

/// A ListItem that contains data to display a message.
class BookItem implements ListItem {
  final Book book;

  BookItem(this.book);

  @override
  Widget build(BuildContext context) => Card(
        shadowColor: Colors.transparent,
        child: Padding(
          padding: const EdgeInsets.all(10.0),
          child: ColoredText(
              PaliScript.getScriptOf(
                  script: context.read<ScriptLanguageProvider>().currentScript,
                  romanText: book.name),
              style: TextStyle(
                  fontSize: Prefs.uiFontSize + 4,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).primaryColor,
                  fontFamily: FontUtils.getfontName(
                      script: context
                          .read<ScriptLanguageProvider>()
                          .currentScript))),
        ),
      );
}
