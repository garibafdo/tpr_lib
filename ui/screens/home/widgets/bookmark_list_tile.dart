import 'package:flutter/material.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import 'package:provider/provider.dart';

import '../../../../business_logic/models/bookmark.dart';
import '../../../../services/provider/script_language_provider.dart';
import '../../../../utils/pali_script.dart';
import 'package:tipitaka_pali/l10n/app_localizations.dart';

class BookmarkListTile extends StatelessWidget {
  // final BookmarkPageViewModel bookmarkViewmodel;
  // final int index;

  const BookmarkListTile(
      {super.key, required this.bookmark, this.onTap, this.onDelete});
  final Bookmark bookmark;
  final Function(Bookmark bookmark)? onDelete;
  final Function(Bookmark bookmark)? onTap;

  @override
  Widget build(BuildContext context) {
    return Slidable(
        startActionPane: ActionPane(
          motion: const DrawerMotion(),
          extentRatio: 0.25,
          children: [
            SlidableAction(
              //label: 'Archive',
              backgroundColor: Colors.red,
              icon: Icons.delete,
              onPressed: (context) {
                if (onDelete != null) onDelete!(bookmark);
              },
            ),
          ],
        ),
        child: Builder(
            builder: (context) => ListTile(
                  onLongPress: () {
                    openSlidable(context);
                  },
                  onTap: () {
                    if (onTap != null) onTap!(bookmark);
                  },
                  title: Text(bookmark.note),
                  subtitle: Text(PaliScript.getScriptOf(
                      script:
                          context.read<ScriptLanguageProvider>().currentScript,
                      romanText: bookmark.name)),
                  trailing: SizedBox(
                    width: 100,
                    child: Row(
                      children: [
                        Text('${AppLocalizations.of(context)!.page} -'),
                        Expanded(
                            child: Text(
                                PaliScript.getScriptOf(
                                    script: context
                                        .read<ScriptLanguageProvider>()
                                        .currentScript,
                                    romanText: bookmark.pageNumber.toString()),
                                textAlign: TextAlign.end)),
                      ],
                    ),
                  ),
                )));
  }

  void openSlidable(BuildContext context) {
    final controller = Slidable.of(context)!;
    controller.openStartActionPane();
    final isClosed = controller.actionPaneType.value == ActionPaneType.none;
    if (isClosed) {
      controller.openEndActionPane();
    }
  }
}
