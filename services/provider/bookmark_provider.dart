import 'package:flutter/material.dart';
import 'package:tipitaka_pali/business_logic/models/bookmark.dart';

class BookmarkNotifier with ChangeNotifier {
  List<Bookmark> _bookmarks = [];

  List<Bookmark> get bookmarks {
    return _bookmarks;
  }

  set bookmarks(List<Bookmark> value) {
    _bookmarks = value;
    notifyListeners();
  }

  Future<void> addBookmark(String bookID, String note, int page) async {
    _bookmarks.add(Bookmark(bookID: bookID, note: note, pageNumber: page));
    notifyListeners();
  }

  Future<void> delete(String bookmarkId) async {
    // Update the local list
    _bookmarks.removeWhere((bookmark) => bookmark.id == bookmarkId);
    notifyListeners();
  }

  Future<void> deleteAll() async {
    // Get reference to all bookmarks

    // Clear the local list
    _bookmarks.clear();
    notifyListeners();
  }
}
