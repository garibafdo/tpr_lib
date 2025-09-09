import 'package:flutter/material.dart';
import 'package:tipitaka_pali/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:tipitaka_pali/data/constants.dart';
import 'package:tipitaka_pali/providers/navigation_provider.dart';

class DeskTopNavigationBar extends StatelessWidget {
  const DeskTopNavigationBar({
    super.key,
    // required this.selectedIndex,
    // this.onDestinationSelected,
  });

  // final int selectedIndex;
  // final ValueChanged<int>? onDestinationSelected;

  @override
  Widget build(BuildContext context) {
    const padding = EdgeInsets.zero;

    final currentNaviagtionItem = context
        .select<NavigationProvider, int>((value) => value.currentNavigation);

    return NavigationRail(
      minWidth: navigationBarWidth,
      leading: Ink.image(
        height: navigationBarWidth,
        width: navigationBarWidth,
        image: const AssetImage('assets/icon/icon.png'),
        fit: BoxFit.scaleDown,
      ),
      useIndicator: true,
      labelType: NavigationRailLabelType.none,
      destinations: [
        NavigationRailDestination(
          icon: Tooltip(
              message: AppLocalizations.of(context)!.home,
              child: const Icon(Icons.home_outlined)),
          selectedIcon: const Icon(Icons.home),
          label: Text(AppLocalizations.of(context)!.home),
          padding: padding,
        ),
        NavigationRailDestination(
          icon: Tooltip(
              message: AppLocalizations.of(context)!.recent,
              child: const Icon(Icons.history_outlined)),
          selectedIcon: const Icon(Icons.history),
          label: Text(AppLocalizations.of(context)!.recent),
          padding: padding,
        ),
        NavigationRailDestination(
          icon: Tooltip(
              message: AppLocalizations.of(context)!.bookmark,
              child: const Icon(Icons.bookmark_outline)),
          selectedIcon: const Icon(Icons.bookmark),
          label: Text(AppLocalizations.of(context)!.bookmark),
          padding: padding,
        ),
        NavigationRailDestination(
          icon: Tooltip(
              message: AppLocalizations.of(context)!.search,
              child: const Icon(Icons.search)),
          selectedIcon: const Icon(Icons.search_outlined),
          label: Text(AppLocalizations.of(context)!.search),
          padding: padding,
        ),
        NavigationRailDestination(
          icon: Tooltip(
              message: AppLocalizations.of(context)!.dictionary,
              child: Image.asset("assets/icon/tpr_dictionary.png",
                  width: 24,
                  height: 24,
                  color: Theme.of(context).iconTheme.color)),
          selectedIcon: Tooltip(
              message: AppLocalizations.of(context)!.dictionary,
              child: Image.asset(
                "assets/icon/tpr_dictionary.png",
                width: 24,
                height: 24,
                color: Theme.of(context).primaryColor,
              )),
          label: Text(AppLocalizations.of(context)!.dictionary),
          padding: padding,
        ),
        NavigationRailDestination(
          icon: Tooltip(
              message: AppLocalizations.of(context)!.settings,
              child: const Icon(Icons.settings_outlined)),
          selectedIcon: const Icon(Icons.settings),
          label: Text(AppLocalizations.of(context)!.settings),
          padding: padding,
        ),
      ],
      // labelType: NavigationRailLabelType.all,
      selectedIndex: currentNaviagtionItem,
      onDestinationSelected: (index) =>
          context.read<NavigationProvider>().onClickedNavigationItem(index),
    );
  }
}
