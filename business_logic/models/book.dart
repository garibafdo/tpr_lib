class Book {
  String id;
  String name;
  int firstPage;
  int lastPage;
  int paraNum;

  Book(
      {required this.id,
      required this.name,
      this.firstPage = 0,
      this.lastPage = 0,
      this.paraNum = 0});

  @override
  String toString() {
    return 'Book #$id $name';
  }
}
