import 'dart:convert';

List<QuickJump> quickJumpFromJson(String str) =>
    List<QuickJump>.from(json.decode(str).map((x) => QuickJump.fromJson(x)));

String quickJumpToJson(List<QuickJump> data) =>
    json.encode(List<dynamic>.from(data.map((x) => x.toJson())));

class QuickJump {
  String qjID;
  String bookID;
  int pageNumber;
  int paragraphNumber;

  QuickJump(
      {required this.qjID,
      this.bookID = "",
      this.pageNumber = 0,
      this.paragraphNumber = 0});

  factory QuickJump.fromJson(Map<dynamic, dynamic> json) {
    return QuickJump(
      qjID: json["qj_id"] ?? "n/a",
      bookID: json["book_id"] ?? "n/a",
      pageNumber: json["page"] ?? 0,
      paragraphNumber: json["paragraph"] ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        "qj_id": qjID,
        "book_id": bookID,
        "page": pageNumber,
        "paragraph": paragraphNumber,
      };

  @override
  String toString() {
    return '$qjID: Page: $pageNumber Paragraph: $paragraphNumber';
  }
}
