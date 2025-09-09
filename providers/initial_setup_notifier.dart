import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

class InitialSetupNotifier extends ChangeNotifier {
  String _status = '';
  int stepsCompleted = 0;

  String get status => _status;
  bool _setupIsFinished = false;

  set setupIsFinished(isFinished) {
    _setupIsFinished = isFinished;
    if (_setupIsFinished) {
      notifyListeners();
    }
  }

  bool get setupIsFinished => _setupIsFinished;

  set status(String message) {
    _status = message;
    notifyListeners();
  }
}
