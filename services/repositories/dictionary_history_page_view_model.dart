// import 'package:flutter/material.dart';
// import '../../business_logic/models/dictionary_history.dart';
// import 'dictionary_history_repo.dart';

// class DictionaryHistoryPageViewModel extends ChangeNotifier {
//   final DictionaryHistoryRepository repository;
//   DictionaryHistoryPageViewModel(this.repository);
//   //
//   List<DictionaryHistory> _recents = [];
//   List<DictionaryHistory> get recents => _recents;

//   Future<void> getDictionaryHistory() async {
//     _recents = await repository.getDictionaryHistory();
//     notifyListeners();
//   }

//   Future<void> delete(DictionaryHistory recent) async {
//     _recents.remove(recent);
//     notifyListeners();
//     await repository.delete(recent);
//   }

//   Future<void> deleteAll() async {
//     _recents.clear();
//     notifyListeners();
//     await repository.deleteAll();
//   }

//   void openBook(DictionaryHistory recent, BuildContext context) async {
// /*    final book = Book(id: recent.bookID, name: recent.bookName!);
//     final openningBookProvider = context.read<OpenningBooksProvider>();
//     openningBookProvider.add(book: book, currentPage: recent.pageNumber);

//     if (Mobile.isPhone(context)) {
//       // Navigator.pushNamed(context, readerRoute,
//       //     arguments: {'book': bookItem.book});
//       Navigator.push(context,
//           MaterialPageRoute(builder: (_) => const MobileReaderContrainer()));
//     }

//     // update recents
//     _recents = await repository.getRecents();
//     notifyListeners();
// */
//   }
// }
