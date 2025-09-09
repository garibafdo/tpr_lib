import 'package:flutter/material.dart';
import 'package:tipitaka_pali/services/prefs.dart';

class UserNotifier extends ChangeNotifier {
  bool get isSignedIn => Prefs.isSignedIn;
  bool get isSignedOut => !Prefs.isSignedIn;
  String _message = "";
  set message(String value) {
    _message = value;
    notifyListeners();
  }

  String get message => _message;

  void setSignedIn(bool value) {
    Prefs.isSignedIn = value;
    notifyListeners();
  }
}
