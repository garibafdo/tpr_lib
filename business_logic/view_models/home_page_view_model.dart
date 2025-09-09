import 'package:tipitaka_pali/business_logic/models/list_item.dart';
import 'package:tipitaka_pali/services/database/database_helper.dart';
import 'package:tipitaka_pali/services/repositories/book_repo.dart';
import 'package:tipitaka_pali/services/repositories/category_repo.dart';

class HomePageViewModel {
  Future<List<ListItem>> fecthItems(String mainCategory) async {
    final databaseProvider = DatabaseHelper();
    List<ListItem> listItems = [];
    final subCategories = await CategoryDatabaseRepository(databaseProvider)
        .getCategories(mainCategory);

    for (int i = 0; i < subCategories.length; ++i) {
      listItems.add(CategoryItem(subCategories[i]));
      final books = await BookDatabaseRepository(databaseProvider)
          .getBooks(mainCategory, subCategories[i].id);
      final bookListItems = books.map((book) => BookItem(book)).toList();
      listItems.addAll(bookListItems);
    }
    return listItems;
  }
}
