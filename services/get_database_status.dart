import 'package:tipitaka_pali/data/constants.dart';
import 'package:tipitaka_pali/services/prefs.dart';

enum DatabaseStatus { uptoDate, outOfDate, notExist }

DatabaseStatus getDatabaseStatus() {
  final isExist = Prefs.isDatabaseSaved;
  if (!isExist) return DatabaseStatus.notExist;

  final dbVersion = Prefs.databaseVersion;
  if (DatabaseInfo.version == dbVersion) return DatabaseStatus.uptoDate;

  return DatabaseStatus.outOfDate;
}
