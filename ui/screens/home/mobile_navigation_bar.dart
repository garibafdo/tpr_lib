import 'package:flutter/material.dart';
import 'package:tipitaka_pali/l10n/app_localizations.dart';
import 'package:tipitaka_pali/providers/navigation_provider.dart';
import 'package:provider/provider.dart';

class MobileNavigationBar extends StatelessWidget {
  const MobileNavigationBar({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final currentNaviagtionItem = context
        .select<NavigationProvider, int>((value) => value.currentNavigation);

    return NavigationBar(
      destinations: [
        NavigationDestination(
          label: AppLocalizations.of(context)!.home,
          icon: const Icon(Icons.home_outlined),
          selectedIcon: const Icon(Icons.home),
        ),
        NavigationDestination(
          label: AppLocalizations.of(context)!.recent,
          icon: const Icon(Icons.history_outlined),
          selectedIcon: const Icon(Icons.history),
        ),
        NavigationDestination(
          label: AppLocalizations.of(context)!.bookmark,
          icon: const Icon(Icons.bookmark_outline),
          selectedIcon: const Icon(Icons.bookmark),
        ),
        NavigationDestination(
          label: AppLocalizations.of(context)!.search,
          icon: const Icon(Icons.search),
          selectedIcon: const Icon(Icons.search),
        ),
        NavigationDestination(
          label: AppLocalizations.of(context)!.dictionary,
          icon: Image.asset(
            "assets/icon/tpr_dictionary.png",
            color: Theme.of(context).iconTheme.color,
            height: 24,
            width: 24,
          ),
          selectedIcon: Image.asset(
            "assets/icon/tpr_dictionary.png",
            width: 24,
            height: 24,
            color: Theme.of(context).iconTheme.color,
          ),
        ),
      ],
      selectedIndex: currentNaviagtionItem,
      onDestinationSelected: (index) =>
          context.read<NavigationProvider>().onClickedNavigationItem(index),
    );
  }
}
