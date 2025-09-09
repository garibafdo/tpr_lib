import 'dart:convert';

List<DpdCompoundFamily> definitionFromJson(String str) => List<DpdCompoundFamily>.from(
    json.decode(str).map((x) => DpdCompoundFamily.fromJson(x)));

class DpdCompoundFamily {
  String compoundFamily;
  String data;
  int count;
  String word;

  DpdCompoundFamily(
      {this.compoundFamily = "",
      this.data = "",
      this.count = 0,
      this.word = ""});

  factory DpdCompoundFamily.fromJson(Map<dynamic, dynamic> json) {
    return DpdCompoundFamily(
      compoundFamily: json["compound_family"] ?? 0,
      data: json["data"] ?? "n/a",
      count: json["count"] ?? 0,
      word: json["word"] ?? "",
    );
  }
}
