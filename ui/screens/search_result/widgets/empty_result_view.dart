import 'package:flutter/material.dart';

class EmptyResultView extends StatelessWidget {
  const EmptyResultView({super.key, required this.searchWord});
  final String searchWord;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: Center(child: Text('Cannot find $searchWord.')),
    );
  }
}
