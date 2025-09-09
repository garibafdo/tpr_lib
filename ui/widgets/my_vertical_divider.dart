import 'package:flutter/material.dart';

class MyVerticalDivider extends StatelessWidget {
  const MyVerticalDivider({super.key, required this.width});
  final double width;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(color: Colors.grey.withOpacity(0.5), blurRadius: 2)
        ],
      ),
    );
  }
}
