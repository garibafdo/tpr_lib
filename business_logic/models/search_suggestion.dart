import 'dart:convert';

List<SearchSuggestion> searchSuggestionFromJson(String str) =>
    List<SearchSuggestion>.from(
        json.decode(str).map((x) => SearchSuggestion.fromJson(x)));

String searchSuggestionToJson(List<SearchSuggestion> data) =>
    json.encode(List<dynamic>.from(data.map((x) => x.toJson())));

class SearchSuggestion {
  String word;
  int count;
  String plain;

  SearchSuggestion({
    this.word = "",
    this.plain = "",
    this.count = 0,
  });

  factory SearchSuggestion.fromJson(Map<dynamic, dynamic> json) {
    return SearchSuggestion(
      word: json["word"] ?? "n/a",
      plain: json["plain"] ?? "n/a",
      count: json["frequency"] ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        "word": word,
        "plain": plain,
        "frequency": count,
      };

  @override
  String toString() {
    return word;
  }
}
