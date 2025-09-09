import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class ValueListenableListener<T> extends StatefulWidget {
  final ValueListenable<T> valueListenable;
  final Widget child;
  final ValueChanged<T>? onValueChanged;

  const ValueListenableListener({
    super.key,
    required this.valueListenable,
    required this.child,
    this.onValueChanged,
  });

  @override
  State<ValueListenableListener<T>> createState() =>
      _ValueListenableListenerState<T>();
}

class _ValueListenableListenerState<T>
    extends State<ValueListenableListener<T>> {
  late T _value;

  @override
  void initState() {
    super.initState();
    _value = widget.valueListenable.value;
    widget.valueListenable.addListener(_handleValueChanged);
  }

  @override
  void didUpdateWidget(covariant ValueListenableListener<T> oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.valueListenable != widget.valueListenable) {
      oldWidget.valueListenable.removeListener(_handleValueChanged);
      _value = widget.valueListenable.value;
      widget.valueListenable.addListener(_handleValueChanged);
    }
  }

  @override
  void dispose() {
    widget.valueListenable.removeListener(_handleValueChanged);
    super.dispose();
  }

  void _handleValueChanged() {
    final newValue = widget.valueListenable.value;
    if (newValue != _value) {
      _value = newValue;
      widget.onValueChanged?.call(newValue);
    }
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}
