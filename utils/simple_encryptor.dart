import 'dart:convert';
import 'dart:typed_data';
import 'package:crypto/crypto.dart' as crypto;
import 'package:encrypt/encrypt.dart' as encrypt;
import 'package:flutter/material.dart';

class SimpleEncryptor {
  final encrypt.Key key;
  final encrypt.IV iv;

  SimpleEncryptor(String password)
      : key = _deriveKey(password),
        iv = _deriveIV(password);

  static encrypt.Key _deriveKey(String password) {
    // Use a cryptographic hash function like SHA-256
    var keyHash =
        crypto.sha256.convert(utf8.encode('${password}key_salt')).bytes;
    return encrypt.Key(Uint8List.fromList(keyHash.sublist(0, 32)));
  }

  static encrypt.IV _deriveIV(String password) {
    var ivHash = crypto.sha256.convert(utf8.encode('${password}iv_salt')).bytes;
    return encrypt.IV(Uint8List.fromList(ivHash.sublist(0, 16)));
  }

  String encryptText(String text) {
    if (text.isEmpty) {
      return ''; // Return empty string if text is empty
    }
    try {
      final paddedText = _padText(text, 4); // Pad before encryption
      final encrypter = encrypt.Encrypter(encrypt.AES(key));
      return encrypter.encrypt(paddedText, iv: iv).base64;
    } catch (e) {
      debugPrint('Encryption failed: $e');
      return "404"; // Indicate failure, adjust according to your needs
    }
  }

  String decryptText(String encryptedText) {
    if (encryptedText.isEmpty) {
      return ''; // Return empty string if encryptedText is empty
    }
    try {
      final encrypter = encrypt.Encrypter(encrypt.AES(key));
      final decryptedText =
          encrypter.decrypt(encrypt.Encrypted.from64(encryptedText), iv: iv);
      return _removePadding(decryptedText); // Remove padding after decryption
    } catch (e) {
      debugPrint('Decryption failed: $e');
      return "404"; // Return 404 This will work with ints and strings passed in
    }
  }

  String _padText(String text, int divisor) {
    final remainder = text.length % divisor;
    if (remainder == 0) {
      return text; // Already divisible, no need to pad
    } else {
      final paddingLength = divisor - remainder;
      return text.padRight(text.length + paddingLength, ' '); // Pad with spaces
    }
  }

  String _removePadding(String text) {
    return text.trim(); // Trim spaces to remove padding
  }
}
