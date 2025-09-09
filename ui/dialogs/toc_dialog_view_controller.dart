import 'package:flutter/foundation.dart';
import 'package:tipitaka_pali/business_logic/models/toc.dart';
import 'package:tipitaka_pali/services/prefs.dart';
import 'package:tipitaka_pali/services/repositories/toc_repo.dart';

class TocDialogViewController {
  final String bookID;
  final TocRepository tocRepository;

  TocDialogViewController({required this.bookID, required this.tocRepository});

  late final List<Toc> _allTocs;
  final ValueNotifier<List<Toc>?> _tocs = ValueNotifier(null);
  ValueListenable<List<Toc>?> get tocs => _tocs;

  String _filterText = '';
  String get filterText => _filterText;

  void onLoad() async {
    _allTocs = await tocRepository.getTocs(bookID);
    _tocs.value = _allTocs;
  }

  void onFilterChanged(String filter) async {
    _filterText = filter;

    if (filter.isEmpty) {
      _tocs.value = [..._allTocs];
    } else {
      final filteredToc = _allTocs
          .where((element) => matchFilter(element.name, filter))
          .toList();
      _tocs.value = [...filteredToc];
    }
  }

  bool matchFilter(String text, String filter) {
    if (Prefs.isFuzzy) {
      return normalizeText(text).contains(normalizeText(filter));
    } else {
      return text.toLowerCase().contains(filter.toLowerCase());
    }
  }

  String normalizeText(String text) {
    // Add any other normalizations as needed
    return text.replaceAllMapped(RegExp('[ṭḍṃāūīḷñṅ]'), (match) {
      return {
        'ṭ': 't',
        'ḍ': 'd',
        'ṃ': 'm',
        'ā': 'a',
        'ū': 'u',
        'ī': 'i',
        'ḷ': 'l',
        'ñ': 'n',
        'ṅ': 'n',
      }[match.group(0)]!;
    }).toLowerCase();
  }
}
