import 'dart:convert';

List<DpdRootFamily> definitionFromJson(String str) => List<DpdRootFamily>.from(
    json.decode(str).map((x) => DpdRootFamily.fromJson(x)));

class DpdRootFamily {
  String rootFamilyKey;
  String rootKey;
  String rootFamily;
  String rootMeaning;
  String data;
  int count;
  String word;

  DpdRootFamily(
      {this.rootFamilyKey = "",
      this.rootKey = "",
      this.rootFamily = "",
      this.rootMeaning = "",
      this.data = "",
      this.count = 0,
      this.word = ""});

  factory DpdRootFamily.fromJson(Map<dynamic, dynamic> json) {
    return DpdRootFamily(
      rootFamilyKey: json["root_family_key"] ?? 0,
      rootKey: json["root_key"] ?? "n/a",
      rootFamily: json["root_family"] ?? "n/a",
      rootMeaning: json["root_meaning"] ?? "n/a",
      data: json["data"] ?? "n/a",
      count: json["count"] ?? 0,
      word: json["word"] ?? "",
    );
  }
}
