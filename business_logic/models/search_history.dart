import 'dart:convert';

class SearchHistory {
  final String word;
  final DateTime dateTime;

  SearchHistory({
    required this.word,
    required this.dateTime,
  });

  SearchHistory copyWith({
    String? word,
    DateTime? dateTime,
  }) {
    return SearchHistory(
      word: word ?? this.word,
      dateTime: dateTime ?? this.dateTime,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'word': word,
      'date': dateTime.toIso8601String(),
    };
  }

  factory SearchHistory.fromMap(Map<String, dynamic> map) {
    return SearchHistory(
      word: map['word'] ?? '',
      dateTime: DateTime.parse(map['date'],),
    );
  }

  String toJson() => json.encode(toMap());

  factory SearchHistory.fromJson(String source) => SearchHistory.fromMap(json.decode(source));

  @override
  String toString() => word;

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
  
    return other is SearchHistory &&
      other.word == word &&
      other.dateTime == dateTime;
  }

  @override
  int get hashCode => word.hashCode ^ dateTime.hashCode;
}
