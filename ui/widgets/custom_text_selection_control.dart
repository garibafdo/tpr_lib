import 'package:flutter/material.dart';

/// This package allows you to create custom text selection controls and use them in the SelectableText widget or in the TextForm or TextFormField widgets.
///
/// Example 1:
/// ```dart
/// SelectionArea(
///  ...,
///  selectionControls: FlutterSelectionControls(
///   toolBarItems: <ToolBarItem>[
///       ToolBarItem(
///         item: Text('Copy'),
///         itemControl: ToolBarItemControl.copy,
///       ),
///       ToolBarItem(
///         item: Text('Share'),
///         onItemPressed: (selectedText) {
///           print(selectedText);
///         },
///       ),
/// ]
///  ),
/// child: Text('Hello World')
/// ...
/// )
///```
/// )
///
/*class FlutterSelectionControls extends MaterialTextSelectionControls {
  /// FlutterSelectionControls takes a list of ToolBarItem(s) as arguments
  /// The ToolBarItems takes a widget as an argument and it will be shown on the tool bar when the text is selected
  ///
  ///
  FlutterSelectionControls(
      {required this.toolBarItems,
      this.horizontalPadding = 16,
      this.verticalPadding = 10})
      : assert(toolBarItems.isNotEmpty);
  final List<ToolBarItem> toolBarItems;

  /// This controls the amount of horizontal space between each tool bar item
  final double horizontalPadding;

  /// This controls the amount of vertical space between each tool bar item and the text selection tool bar
  final double verticalPadding;
  // This controlls the padding between the toolbar and the anchor.
  static const double _kToolbarContentDistanceBelow = 20.0;
  static const double _kToolbarContentDistance = 8.0;

  /// This is called when a [ToolBarItem] is tapped or pressed
  void _onItemSelected({
    required ToolBarItem item,
    required TextSelectionDelegate delegate,
    required ClipboardStatusNotifier? clipboardStatus,
  }) async {
    /// Handles the callback if the itemControl was passed as an argument to the pressed [ToolBarItem]
    if (item.itemControl != null) {
      final ToolBarItemControl control = item.itemControl!;
/*
      /// Handle the callback if the itemControl passed is of type [ToolBarItemControl.copy]
      if (control == ToolBarItemControl.copy) {
        if (canCopy(delegate)) return handleCopy(delegate, clipboardStatus);
        return;
      }

      /// Handle the callback if the itemControl passed is of type [ToolBarItemControl.selectAll]
      if (control == ToolBarItemControl.selectAll) {
        if (canSelectAll(delegate)) return handleSelectAll(delegate);
        return;
      }

      /// Handle the callback if the itemControl passed is of type [ToolBarItemControl.paste]
      if (control == ToolBarItemControl.paste) {
        if (canPaste(delegate)) return handlePaste(delegate);
        return;
      }

      /// Handle the callback if the itemControl passed is of type [ToolBarItemControl.cut]
      if (control == ToolBarItemControl.cut) {
        if (canCut(delegate)) return handleCut(delegate, clipboardStatus);
        return;
      }
      return;
    }

    /// If the argument [onItemPressed] was passed instead of the [itemControl] argument...
    /// ..we return a [void Function(String)] which will have:
    /// 1. The Highlighted Text
    ///

    // Todo extract text from given delegate
    // i can't extract text from delegate
    // here is a hcak
    // 1) copy to clipboard
    // 2) get text back from clipboard
    // 3) send to onItemPressed callback

    if (canCopy(delegate)) {
      handleCopy(delegate);
      final clipboardData = Clipboard.getData('text/plain');
      clipboardData.then((value) {
        delegate.hideToolbar();
        if (value != null && value.text != null) {
          item.onItemPressed?.call(value.text!);
        }
      });
    }
    */
  }

  /// Builder for material-style copy/paste text selection toolbar.
  @override
  Widget buildToolbar(
    BuildContext context,
    Rect globalEditableRegion,
    double textLineHeight,
    Offset selectionMidpoint,
    List<TextSelectionPoint> endpoints,
    TextSelectionDelegate delegate,
    ClipboardStatusNotifier? clipboardStatus,
    Offset? lastSecondaryTapDownPosition,
  ) {
    final TextSelectionPoint startTextSelectionPoint = endpoints[0];
    final TextSelectionPoint endTextSelectionPoint =
        endpoints.length > 1 ? endpoints[1] : endpoints[0];
    final Offset anchorAbove = Offset(
        globalEditableRegion.left + (selectionMidpoint).dx,
        globalEditableRegion.top +
            startTextSelectionPoint.point.dy -
            textLineHeight -
            _kToolbarContentDistance);
    final Offset anchorBelow = Offset(
      globalEditableRegion.left + (selectionMidpoint).dx,
      globalEditableRegion.top +
          endTextSelectionPoint.point.dy +
          _kToolbarContentDistanceBelow,
    );
    return _SelectionToolBar(
        anchorAbove: anchorAbove,
        anchorBelow: anchorBelow,
        clipboardStatus: clipboardStatus,
        toolBarItems: toolBarItems,
        horizontalPadding: horizontalPadding,
        verticalPadding: verticalPadding,
        canCopy: canCopy(delegate),
        canCut: canCut(delegate),
        canPaste: canPaste(delegate),
        canSelectAll: canSelectAll(delegate),
        onItemSelected: (ToolBarItem item) => _onItemSelected(
            item: item, delegate: delegate, clipboardStatus: clipboardStatus));
  }
}
*/
class _SelectionToolBar extends StatefulWidget {
  const _SelectionToolBar(
      {required this.anchorAbove,
      required this.anchorBelow,
      required this.clipboardStatus,
      required this.toolBarItems,
      required this.onItemSelected,
      required this.horizontalPadding,
      required this.verticalPadding,
      required this.canCopy,
      required this.canCut,
      required this.canPaste,
      required this.canSelectAll});

  /// The focal point above which the toolbar attempts to position itself.
  final Offset anchorAbove;

  /// The focal point below which the toolbar attempts to position itself, if it doesn't fit above [anchorAbove].
  final Offset anchorBelow;

  ///A [ValueNotifier] whose [value] indicates whether the current contents of the clipboard can be pasted.
  final ClipboardStatusNotifier? clipboardStatus;

  /// Widgets to be displayed on the text selection tool bar
  final List<ToolBarItem> toolBarItems;

  /// A callback function when a [ToolBarItem] is pressed
  final Function(ToolBarItem) onItemSelected;

  /// This controls the amount of vertical space between each tool bar item
  final double horizontalPadding;

  /// This controls the amount of vertical space between each tool bar item and the text selection tool bar
  final double verticalPadding;

  /// Check if the highlighted text can be copied
  final bool canCopy;

  /// Check if the highlighted text can be cut
  final bool canCut;

  /// Check if paste command can be executed
  final bool canPaste;

  /// Check if select all command can be executed
  final bool canSelectAll;
  @override
  __SelectionToolBarState createState() => __SelectionToolBarState();
}

class __SelectionToolBarState extends State<_SelectionToolBar> {
  void _onChangedClipboardStatus() {
    if (mounted) {
      setState(() {
        // Inform the widget that the value of clipboardStatus has changed.
      });
    }
  }

  @override
  void initState() {
    super.initState();
    widget.clipboardStatus?.addListener(_onChangedClipboardStatus);
    widget.clipboardStatus?.update();
  }

  @override
  void didUpdateWidget(_SelectionToolBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    final cs = widget.clipboardStatus;
    if (null == cs) {
      return;
    }
    if (widget.clipboardStatus != oldWidget.clipboardStatus) {
      cs.addListener(_onChangedClipboardStatus);
      oldWidget.clipboardStatus!.removeListener(_onChangedClipboardStatus);
    }
    cs.update();
  }

/*
  @override
  void dispose() {
    super.dispose();
    if (widget.clipboardStatus?.disposed != null &&
        widget.clipboardStatus!.disposed == false) {
      widget.clipboardStatus!.removeListener(_onChangedClipboardStatus);
    }
  }
*/
  @override
  Widget build(BuildContext context) {
    ///TODO GIVE OPTION TO SWITCH BETWEEN CUPERTINO AND MATERIAL TEXT SELECTION TOOL BAR TYPES
    // return CupertinoTextSelectionToolbar(
    //     anchorAbove: widget.anchorAbove,
    //     anchorBelow: widget.anchorBelow,
    //     toolbarBuilder:
    //         (BuildContext context, Offset offset, bool value, Widget child) {
    //       return Card(child: child);
    //     },
    //     children:
    //         widget.toolBarItems.map((item) => itemButton(item: item)).toList());
    return TextSelectionToolbar(
        anchorAbove: widget.anchorAbove,
        anchorBelow: widget.anchorBelow,
        toolbarBuilder: (BuildContext context, Widget child) {
          return Card(child: child);
        },
        children: widget.toolBarItems.map((item) {
          if (item.itemControl != null) {
            if (item.itemControl == ToolBarItemControl.copy &&
                !widget.canCopy) {
              return const SizedBox();
            }
            if (item.itemControl == ToolBarItemControl.cut && !widget.canCut) {
              return const SizedBox();
            }
            if (item.itemControl == ToolBarItemControl.paste &&
                !widget.canPaste) return const SizedBox();
            if (item.itemControl == ToolBarItemControl.selectAll &&
                !widget.canSelectAll) return const SizedBox();
          }
          return itemButton(
              item: item,
              horizontalPadding: widget.horizontalPadding,
              verticalPadding: widget.verticalPadding);
        }).toList());
  }

  Widget itemButton(
      {required ToolBarItem item,
      required double horizontalPadding,
      required double verticalPadding}) {
    return InkWell(
      onTap: () => widget.onItemSelected(item),
      child: Padding(
        padding: EdgeInsets.symmetric(
            vertical: verticalPadding, horizontal: horizontalPadding),
        child: item.item,
      ),
    );
  }
}

/// ToolBarItem
/// This requires a widget[item] which will be shown on the text selection tool bar when a text is highlighted
/// This class also gives you an option to choose between...
/// ... flutter text selection controls[copy, paste, cut, select all] or custom controls
class ToolBarItem {
  ToolBarItem({required this.item, this.onItemPressed, this.itemControl})
      : assert(
            onItemPressed == null ? itemControl != null : itemControl == null);

  /// The widget which will be shown on the text selection tool bar when a text is highlighted
  final Widget item;

  /// This gives access the highlighted text, the start index and the end index of the highlighted text
  final Function(String selectedText)? onItemPressed;

  /// This gives you the option to use flutter text selection controls on your custom widget
  /// For instance, instead of having the text [Copy] on the tool bar,...
  /// ...you can have the [Icon(Icons.copy)] as the widget...
  /// ...and use [ToolBarItemControl.copy] control to copy the highlighted text when the icon is tapped
  final ToolBarItemControl? itemControl;
}

enum ToolBarItemControl { copy, paste, cut, selectAll }
