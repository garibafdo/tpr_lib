import 'package:tipitaka_pali/business_logic/models/dictionary_history.dart';
import 'package:tipitaka_pali/services/database/database_helper.dart';

abstract class DictionaryHistoryRepository {
  Future<int> insert(
    String word,
    String context,
    int page,
    String bookID,
  );

  Future<int> delete(String word);

  Future<void> deleteAll();

  Future<List<DictionaryHistory>> getAll();
}

class DictionaryHistoryDatabaseRepository
    implements DictionaryHistoryRepository {
  DictionaryHistoryDatabaseRepository({required this.dbh});
  DatabaseHelper dbh;

  final _historyTable = 'dictionary_history';
  final _columnWord = 'word';

  @override
  Future<int> insert(
      String word, String context, int page, String bookId) async {
    final db = await dbh.database;
    // delete first if exists
    await db
        .delete(_historyTable, where: '$_columnWord = ?', whereArgs: [word]);

    // Remove numbers and punctuation, retaining only specified characters and whitespace
    String sanitizedWord =
        word.replaceAll(RegExp(r'[^\sa-zA-ZāīūṅñṭḍṇḷṃĀĪŪṄÑṬḌṆḶṂ]+'), '');

    return await db.insert(
      _historyTable,
      DictionaryHistory(
              word: sanitizedWord,
              context: context,
              bookId: bookId,
              page: page,
              dateTime: DateTime.now())
          .toMap(),
    );
  }

  @override
  Future<int> delete(String word) async {
    final db = await dbh.database;
    return await db
        .delete(_historyTable, where: '$_columnWord = ?', whereArgs: [word]);
  }

  @override
  Future<void> deleteAll() async {
    final db = await dbh.database;
    await db.delete(_historyTable);
  }

  @override
  Future<List<DictionaryHistory>> getAll() async {
    final db = await dbh.database;
    final maps = await db.query(
      _historyTable,
    );
    return maps.map((entry) => DictionaryHistory.fromMap(entry)).toList();
  }
}
