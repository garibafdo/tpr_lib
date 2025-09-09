import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../services/database/database_helper.dart';
import '../../services/repositories/dictionary_history_repo.dart';
import '../../services/repositories/dictionary_repo.dart';
import '../screens/dictionary/controller/dictionary_controller.dart';
import '../screens/dictionary/widget/dict_algo_selector.dart';
import '../screens/dictionary/widget/dict_content_view.dart';
import '../screens/dictionary/widget/dict_search_field.dart';

class DictionaryDialog extends StatelessWidget {
  final String? word;
  final ScrollController? scrollController;

  const DictionaryDialog({super.key, this.word, this.scrollController});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<DictionaryController>(
      create: (context) => DictionaryController(
          context: context,
          dictionaryRepository: DictionaryDatabaseRepository(DatabaseHelper()),
          dictionaryHistoryRepository: DictionaryHistoryDatabaseRepository(
            dbh: DatabaseHelper(),
          ),
          lookupWord: word)
        ..onLoad(),
      child: Consumer<DictionaryController>(
        builder: (context, dc, __) {
          return Material(
            child: Column(
              // mainAxisSize: MainAxisSize.min,
              children: [
                // topbar
                Row(
                  children: [
                    IconButton(
                        onPressed: () => Navigator.pop(context),
                        icon: const Icon(Icons.close)),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios),
                      onPressed: () => dc.onClickedPrevious(),
                    ),
                    IconButton(
                      icon: const Icon(Icons.arrow_forward_ios),
                      onPressed: () => dc.onClickedNext(),
                    ),
                    IconButton(
                        onPressed: dc.onClickedHistoryButton,
                        icon: const Icon(Icons.history)),
                  ],
                ),
                // search field
                const Row(
                  children: [
                    Expanded(child: DictionarySearchField()),
                    Padding(
                      padding: EdgeInsets.all(8.0),
                      child: DictionaryAlgorithmModeView(),
                    ),
                  ],
                ),
                // main content view
                Expanded(
                  child: DictionaryContentView(
                    scrollController: scrollController,
                  ),
                ),
                const SizedBox(height: 60),
              ],
            ),
          );
        },
      ),
    );
  }
}
