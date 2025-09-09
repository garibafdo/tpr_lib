class TprMessage {
  final String generalMessage;
  final String generalMessageDate;
  final String androidVersion;
  final String androidMessage;
  final String androidMessageDate;
  final String androidPeuDate;
  final String androidDpdDate;
  final String iosVersion;
  final String iosMessage;
  final String iosMessageDate;
  final String iosPeuDate;
  final String iosDpdDate;
  final String windowsVersion;
  final String windowsMessage;
  final String windowsMessageDate;
  final String windowsPeuDate;
  final String windowsDpdDate;
  final String macOsVersion;
  final String macOsMessage;
  final String macOsMessageDate;
  final String macOsPeuDate;
  final String macOsDpdDate;
  final String linuxVersion;
  final String linuxMessage;
  final String linuxMessageDate;
  final String linuxPeuDate;
  final String linuxDpdDate;

  TprMessage({
    this.generalMessage = '',
    this.generalMessageDate = '',
    this.androidVersion = '',
    this.androidMessage = '',
    this.androidMessageDate = '',
    this.androidPeuDate = '',
    this.androidDpdDate = '',
    this.iosVersion = '',
    this.iosMessage = '',
    this.iosMessageDate = '',
    this.iosPeuDate = '',
    this.iosDpdDate = '',
    this.windowsVersion = '',
    this.windowsMessage = '',
    this.windowsMessageDate = '',
    this.windowsPeuDate = '',
    this.windowsDpdDate = '',
    this.macOsVersion = '',
    this.macOsMessage = '',
    this.macOsMessageDate = '',
    this.macOsPeuDate = '',
    this.macOsDpdDate = '',
    this.linuxVersion = '',
    this.linuxMessage = '',
    this.linuxMessageDate = '',
    this.linuxPeuDate = '',
    this.linuxDpdDate = '',
  });

  factory TprMessage.fromJson(Map<String, dynamic> json) {
    return TprMessage(
      generalMessage: json['general']['message'] ?? '',
      generalMessageDate: json['general']['messageDate'] ?? '',
      androidVersion: json['android']['currentVersion'] ?? '',
      androidMessage: json['android']['message'] ?? '',
      androidMessageDate: json['android']['messageDate'] ?? '',
      androidPeuDate: json['android']['peuDate'] ?? '',
      androidDpdDate: json['android']['dpdDate'] ?? '',
      iosVersion: json['ios']['currentVersion'] ?? '',
      iosMessage: json['ios']['message'] ?? '',
      iosMessageDate: json['ios']['messageDate'] ?? '',
      iosPeuDate: json['ios']['peuDate'] ?? '',
      iosDpdDate: json['ios']['dpdDate'] ?? '',
      windowsVersion: json['windows']['currentVersion'] ?? '',
      windowsMessage: json['windows']['message'] ?? '',
      windowsMessageDate: json['windows']['messageDate'] ?? '',
      windowsPeuDate: json['windows']['peuDate'] ?? '',
      windowsDpdDate: json['windows']['dpdDate'] ?? '',
      macOsVersion: json['macos']['currentVersion'] ?? '',
      macOsMessage: json['macos']['message'] ?? '',
      macOsMessageDate: json['macos']['messageDate'] ?? '',
      macOsPeuDate: json['macos']['peuDate'] ?? '',
      macOsDpdDate: json['macos']['dpdDate'] ?? '',
      linuxVersion: json['linux']['currentVersion'] ?? '',
      linuxMessage: json['linux']['message'] ?? '',
      linuxMessageDate: json['linux']['messageDate'] ?? '',
      linuxPeuDate: json['linux']['peuDate'] ?? '',
      linuxDpdDate: json['linux']['dpdDate'] ?? '',
    );
  }
}
