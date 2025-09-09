import 'dart:convert';

List<DpdInflection> definitionFromJson(String str) => List<DpdInflection>.from(
    json.decode(str).map((x) => DpdInflection.fromJson(x)));

class DpdInflection {
  int id;
  String stem;
  String pattern;
  String inflections;
  String word;

  DpdInflection(
      {this.id = 0,
      this.stem = "",
      this.pattern = "",
      this.inflections = "",
      this.word = ""});

  factory DpdInflection.fromJson(Map<dynamic, dynamic> json) {
    return DpdInflection(
      id: json["id"] ?? 0,
      stem: json["stem"] ?? "n/a",
      pattern: json["pattern"] ?? "n/a",
      inflections: json["inflections"] ?? "n/a",
      word: json["word"] ?? "n/a",
    );
  }
}
