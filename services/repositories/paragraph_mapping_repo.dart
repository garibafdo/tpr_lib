import 'package:flutter/material.dart';
import 'package:tipitaka_pali/business_logic/models/paragraph_mapping.dart';
import 'package:tipitaka_pali/services/dao/paragraph_mapping_dao.dart';
import 'package:tipitaka_pali/services/database/database_helper.dart';

abstract class ParagraphMappingRepository {
  Future<List<ParagraphMapping>> getParagraphMappings(
      String bookID, int pageNumber);

  Future<List<ParagraphMapping>> getBackWardParagraphMappings(
      String bookID, int pageNumber);
}

class ParagraphMappingDatabaseRepository implements ParagraphMappingRepository {
  final dao = ParagraphMappingDao();
  final DatabaseHelper databaseProvider;
  ParagraphMappingDatabaseRepository(this.databaseProvider);

  @override
  Future<List<ParagraphMapping>> getParagraphMappings(
      String bookID, int pageNumber) async {
    final db = await databaseProvider.database;

    List<Map<String, dynamic>> maps = await db.rawQuery('''
      SELECT ${dao.columnParagraph}, ${dao.columnExpBookID}, ${dao.columnBookName}, ${dao.columnExpPageNumber}
      FROM ${dao.tableParagraphMapping}
      INNER JOIN ${dao.tableBooks} ON ${dao.columnBookID} = 
      ${dao.columnExpBookID}
      WHERE ${dao.columnBaseBookID} = '$bookID' AND 
      ${dao.columnBasePageNumber} = $pageNumber AND 
      ${dao.columnParagraph} != 0
      ''');

    // List<Map> maps = await db.query(dao.tableParagraphMapping,
    //     columns: [dao.columnParagraph, dao.columnExpBookID, dao.columnExpPageNumber],
    //     where:
    //         '${dao.columnBaseBookID} = ? AND ${dao.columnBasePageNumber} = ? AND ${dao.columnParagraph} != ?',
    //     whereArgs: [bookID, pageNumber, 0]);

    return dao.fromList(maps);
  }

  @override
  Future<List<ParagraphMapping>> getBackWardParagraphMappings(
      String bookID, int pageNumber) async {
    final db = await databaseProvider.database;

    final sql = '''
      SELECT ${dao.columnParagraph}, ${dao.columnBaseBookID} as ${dao.columnExpBookID}, ${dao.columnBookName}, ${dao.columnBasePageNumber} as ${dao.columnExpPageNumber}
      FROM ${dao.tableParagraphMapping}
      INNER JOIN ${dao.tableBooks} ON ${dao.columnBookID} = 
      ${dao.columnBaseBookID}
      WHERE ${dao.columnExpBookID} = '$bookID' AND 
      ${dao.columnExpPageNumber} = $pageNumber AND 
      ${dao.columnParagraph} != 0
      ''';

    List<Map<String, dynamic>> maps = await db.rawQuery(sql);

    debugPrint(maps.toString());

    // List<Map> maps = await db.query(dao.tableParagraphMapping,
    //     columns: [dao.columnParagraph, dao.columnExpBookID, dao.columnExpPageNumber],
    //     where:
    //         '${dao.columnBaseBookID} = ? AND ${dao.columnBasePageNumber} = ? AND ${dao.columnParagraph} != ?',
    //     whereArgs: [bookID, pageNumber, 0]);

    return dao.fromList(maps);
  }
}
