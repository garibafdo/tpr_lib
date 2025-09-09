import 'package:tipitaka_pali/services/provider/theme_change_notifier.dart';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tipitaka_pali/services/prefs.dart';

class M3SwitchWidget extends StatelessWidget {
  const M3SwitchWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final localeProvider = Provider.of<ThemeChangeNotifier>(context);

    return Row(
      mainAxisSize: MainAxisSize
          .min, // Ensure the row takes up the minimum space necessary
      children: [
        Switch(
          value: Prefs.useM3,
          onChanged: (newValue) {
            Prefs.useM3 = newValue;
            localeProvider.useM3 = newValue;
          },
        ),
      ],
    );
  }
}
