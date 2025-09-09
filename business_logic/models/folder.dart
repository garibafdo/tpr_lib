// folder.dart

class Folder {
  final int id;
  String name; // can rename
  final int? parentFolderId; // Optional: for nested folders

  Folder({
    required this.id,
    required this.name,
    this.parentFolderId,
  });

  // Factory method to create a Folder object from a Map (e.g., database query result)
  factory Folder.fromJson(Map<String, dynamic> json) {
    if (json['id'] == -1) {
      return Folder(id: json['id'], name: json['name']);
    } else {
      return Folder(
        id: json['id'],
        name: json['name'],
        // If parent_folder_id is -1, treat it as null, otherwise use the actual value
        parentFolderId: json['parent_folder_id'],
      );
    }
  }

  // Method to convert Folder object to Map
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'parent_folder_id': parentFolderId,
    };
  }

  @override
  String toString() {
    return 'Folder{id: $id, name: $name, parentFolderId: $parentFolderId}';
  }
}
