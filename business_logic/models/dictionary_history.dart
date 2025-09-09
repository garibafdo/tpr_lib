import 'dart:convert';

class DictionaryHistory {
  final String word;
  final DateTime dateTime;
  final String context;
  final String bookId;
  final int page;

  DictionaryHistory(
      {required this.word,
      required this.dateTime,
      required this.context,
      required this.bookId,
      required this.page});

  DictionaryHistory copyWith({
    String? word,
    DateTime? dateTime,
    String? context,
    String? bookId,
    int? page,
  }) {
    return DictionaryHistory(
      word: word ?? this.word,
      dateTime: dateTime ?? this.dateTime,
      bookId: bookId ?? this.bookId,
      page: page ?? this.page,
      context: context ?? this.context,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'word': word,
      'date': dateTime.toIso8601String(),
      'page_number': page,
      'book_id': bookId,
      'context': context,
    };
  }

  factory DictionaryHistory.fromMap(Map<String, dynamic> map) {
    return DictionaryHistory(
      word: map['word'] ?? '',
      dateTime: DateTime.parse(
        map['date'],
      ),
      page: map['page'] ?? 0,
      bookId: map['book_id'] ?? '',
      context: map['context'] ?? '',
    );
  }

  String toJson() => json.encode(toMap());

  factory DictionaryHistory.fromJson(String source) =>
      DictionaryHistory.fromMap(json.decode(source));

  @override
  String toString() => word;

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is DictionaryHistory &&
        other.word == word &&
        other.dateTime == dateTime;
  }

  @override
  int get hashCode => word.hashCode ^ dateTime.hashCode;
}
