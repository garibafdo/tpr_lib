import 'dart:convert';

List<Bookmark> bookmarkFromJson(String content) =>
    List<Bookmark>.from(json.decode(content).map((x) => Bookmark.fromJson(x)));

String bookmarkToJson(List<Bookmark> bookmarks) =>
    json.encode(List<dynamic>.from(bookmarks.map((x) => x.toJson())));

class Bookmark {
  final int id;
  final String firestoreId;
  final String bookID;
  final int pageNumber;
  String note;
  String name;
  String selectedText;
  int folderId; // Identifies the folder assignment
  int bmkSort; // Used for sorting bookmarks within a folder

  Bookmark({
    this.id = 0,
    this.firestoreId = "n/a",
    this.bookID = "n/a",
    this.pageNumber = 0,
    this.note = "n/a",
    this.name = 'Unknown',
    this.selectedText = '',
    this.folderId =
        -1, // Default value indicating no specific folder, ensuring backwards compatibility
    this.bmkSort =
        -1, // Default sorting value indicating no specific order, -1 can signify unsorted or default order
  });

  @override

  /*String toString() {
    return '''ID: $id
              Book ID: $bookID
              Page Number: $pageNumber
              Note: $note
              Name: $name
              Selected Text: $selectedText
              Folder ID: $folderId
              Bookmark Sort: $bmkSort
    ''';
  }
  */

  String toString() {
    return '''bookID: $bookID
              name: $name
              pageNumber: $pageNumber
              note: $note
              selected_text: $selectedText
    ''';
    //removed bookname for now.
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'book_id': bookID,
      'firestoreId': firestoreId,
      'page_number': pageNumber,
      'note': note,
      'name': name,
      'selected_text': selectedText,
      'folder_id': folderId,
      'bmk_sort': bmkSort,
    };

    // Include 'id' only if it's not the default value (0), indicating an existing record
    if (id != 0) {
      data['id'] = id;
    }

    return data;
  }

  factory Bookmark.fromJson(Map<String, dynamic> json) {
    int parsedId = 0;
    if (json.containsKey('id')) {
      // Attempt to parse 'id' as int, regardless of its original type in JSON
      parsedId = int.tryParse(json['id'].toString()) ?? 0;
    }
    return Bookmark(
      id: parsedId,
      firestoreId: json['firestoreId'] ?? 'n/a',
      bookID: json['book_id'] ?? 'n/a',
      pageNumber: json['page_number'] ?? 0,
      note: json['note'] ?? 'n/a',
      name: json['name'] ?? 'Unknown',
      selectedText: json['selected_text'] ?? '',
      folderId: json['folder_id'] ??
          -1, // Ensure string type; default to '-1' if null
      bmkSort: json['bmk_sort'] ?? -1, // Default to -1 if null or missing
    );
  }
}
