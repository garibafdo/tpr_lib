import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_bn.dart';
import 'app_localizations_ccp.dart';
import 'app_localizations_en.dart';
import 'app_localizations_hi.dart';
import 'app_localizations_it.dart';
import 'app_localizations_km.dart';
import 'app_localizations_lo.dart';
import 'app_localizations_my.dart';
import 'app_localizations_ru.dart';
import 'app_localizations_si.dart';
import 'app_localizations_th.dart';
import 'app_localizations_vi.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('bn'),
    Locale('ccp'),
    Locale('en'),
    Locale('hi'),
    Locale('it'),
    Locale('km'),
    Locale('lo'),
    Locale('my'),
    Locale('ru'),
    Locale('si'),
    Locale('th'),
    Locale('vi'),
    Locale('zh')
  ];

  /// No description provided for @tipitaka_pali_reader.
  ///
  /// In en, this message translates to:
  /// **'Tipitaka Pāḷi Reader'**
  String get tipitaka_pali_reader;

  /// No description provided for @home.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get home;

  /// No description provided for @bookmark.
  ///
  /// In en, this message translates to:
  /// **'Bookmark'**
  String get bookmark;

  /// No description provided for @recent.
  ///
  /// In en, this message translates to:
  /// **'Recent'**
  String get recent;

  /// No description provided for @search.
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get search;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @dictionary.
  ///
  /// In en, this message translates to:
  /// **'Dictionary'**
  String get dictionary;

  /// No description provided for @theme.
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get theme;

  /// No description provided for @darkMode.
  ///
  /// In en, this message translates to:
  /// **'Page'**
  String get darkMode;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @dictionaries.
  ///
  /// In en, this message translates to:
  /// **'Dictionaries'**
  String get dictionaries;

  /// No description provided for @paliScript.
  ///
  /// In en, this message translates to:
  /// **'Pāḷi Script'**
  String get paliScript;

  /// No description provided for @showAlternatePali.
  ///
  /// In en, this message translates to:
  /// **'Show Alternate Pāḷi'**
  String get showAlternatePali;

  /// No description provided for @showPTSPageNumber.
  ///
  /// In en, this message translates to:
  /// **'Show PTS PageNumber'**
  String get showPTSPageNumber;

  /// No description provided for @showThaiPageNumber.
  ///
  /// In en, this message translates to:
  /// **'Show Thai PageNumber'**
  String get showThaiPageNumber;

  /// No description provided for @showVRIPageNumber.
  ///
  /// In en, this message translates to:
  /// **'Show VRI PageNumber'**
  String get showVRIPageNumber;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @unable_open_page.
  ///
  /// In en, this message translates to:
  /// **'Unable to open page for this page.'**
  String get unable_open_page;

  /// No description provided for @enter_note.
  ///
  /// In en, this message translates to:
  /// **'Enter note here'**
  String get enter_note;

  /// No description provided for @save.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @page.
  ///
  /// In en, this message translates to:
  /// **'Page'**
  String get page;

  /// No description provided for @select_paragraph.
  ///
  /// In en, this message translates to:
  /// **'Select paragraph'**
  String get select_paragraph;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @paragraph_number.
  ///
  /// In en, this message translates to:
  /// **'Commentaries of Paragraph'**
  String get paragraph_number;

  /// No description provided for @table_of_contents.
  ///
  /// In en, this message translates to:
  /// **'Table Of Contents'**
  String get table_of_contents;

  /// No description provided for @goto.
  ///
  /// In en, this message translates to:
  /// **'Goto'**
  String get goto;

  /// No description provided for @paragraph.
  ///
  /// In en, this message translates to:
  /// **'Paragraph'**
  String get paragraph;

  /// No description provided for @go.
  ///
  /// In en, this message translates to:
  /// **'Go'**
  String get go;

  /// No description provided for @toc.
  ///
  /// In en, this message translates to:
  /// **'TOC'**
  String get toc;

  /// No description provided for @mat.
  ///
  /// In en, this message translates to:
  /// **'MAT'**
  String get mat;

  /// No description provided for @font.
  ///
  /// In en, this message translates to:
  /// **'Font'**
  String get font;

  /// No description provided for @anywhere.
  ///
  /// In en, this message translates to:
  /// **'Any Part'**
  String get anywhere;

  /// No description provided for @openingBook.
  ///
  /// In en, this message translates to:
  /// **'Opening Books'**
  String get openingBook;

  /// No description provided for @animationSpeed.
  ///
  /// In en, this message translates to:
  /// **'Animation Speed in ms'**
  String get animationSpeed;

  /// No description provided for @generalSettings.
  ///
  /// In en, this message translates to:
  /// **'General'**
  String get generalSettings;

  /// No description provided for @increaseFontSize.
  ///
  /// In en, this message translates to:
  /// **'Increase font size (Ctrl +)'**
  String get increaseFontSize;

  /// No description provided for @decreaseFontSize.
  ///
  /// In en, this message translates to:
  /// **'Decrease font size (Ctrl -)'**
  String get decreaseFontSize;

  /// No description provided for @openLinkedBook.
  ///
  /// In en, this message translates to:
  /// **'Open linked book'**
  String get openLinkedBook;

  /// No description provided for @gotoPageParagraph.
  ///
  /// In en, this message translates to:
  /// **'Goto page or paragraph'**
  String get gotoPageParagraph;

  /// No description provided for @scriptLanguage.
  ///
  /// In en, this message translates to:
  /// **'Script Language'**
  String get scriptLanguage;

  /// No description provided for @dictionaryToClipboard.
  ///
  /// In en, this message translates to:
  /// **'Dictionary to Clipboard'**
  String get dictionaryToClipboard;

  /// No description provided for @help.
  ///
  /// In en, this message translates to:
  /// **'Help'**
  String get help;

  /// No description provided for @reportIssue.
  ///
  /// In en, this message translates to:
  /// **'Report Issue'**
  String get reportIssue;

  /// No description provided for @areSureDelete.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete all items?'**
  String get areSureDelete;

  /// No description provided for @delete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

  /// No description provided for @confirmation.
  ///
  /// In en, this message translates to:
  /// **'Confirmation'**
  String get confirmation;

  /// No description provided for @dictionaryHistory.
  ///
  /// In en, this message translates to:
  /// **'Dictionary History'**
  String get dictionaryHistory;

  /// No description provided for @share.
  ///
  /// In en, this message translates to:
  /// **'Share'**
  String get share;

  /// No description provided for @downloadTitle.
  ///
  /// In en, this message translates to:
  /// **'Download Extended Texts & Dictionaries'**
  String get downloadTitle;

  /// No description provided for @filter.
  ///
  /// In en, this message translates to:
  /// **'Filter'**
  String get filter;

  /// No description provided for @doYouWantToLeave.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to leave the App?  Your opened books be closed.'**
  String get doYouWantToLeave;

  /// No description provided for @yes.
  ///
  /// In en, this message translates to:
  /// **'Yes'**
  String get yes;

  /// No description provided for @no.
  ///
  /// In en, this message translates to:
  /// **'No'**
  String get no;

  /// No description provided for @dictionaryFontSize.
  ///
  /// In en, this message translates to:
  /// **'Dictionary Font Size'**
  String get dictionaryFontSize;

  /// No description provided for @panelSize.
  ///
  /// In en, this message translates to:
  /// **'Panel Size'**
  String get panelSize;

  /// No description provided for @multiViewsMode.
  ///
  /// In en, this message translates to:
  /// **'Multiple Views'**
  String get multiViewsMode;

  /// No description provided for @numVisibleViews.
  ///
  /// In en, this message translates to:
  /// **'Visible Views'**
  String get numVisibleViews;

  /// No description provided for @extensions.
  ///
  /// In en, this message translates to:
  /// **'Extensions'**
  String get extensions;

  /// No description provided for @quickjump.
  ///
  /// In en, this message translates to:
  /// **'Quick Jump'**
  String get quickjump;

  /// No description provided for @shareThisNote.
  ///
  /// In en, this message translates to:
  /// **'Share this note'**
  String get shareThisNote;

  /// No description provided for @shareAllNotes.
  ///
  /// In en, this message translates to:
  /// **'Share all notes'**
  String get shareAllNotes;

  /// No description provided for @shareTitle.
  ///
  /// In en, this message translates to:
  /// **'TPR Bookmark and Note'**
  String get shareTitle;

  /// No description provided for @distanceBetweenWords.
  ///
  /// In en, this message translates to:
  /// **'Distance between words'**
  String get distanceBetweenWords;

  /// No description provided for @exact.
  ///
  /// In en, this message translates to:
  /// **'exact'**
  String get exact;

  /// No description provided for @prefix.
  ///
  /// In en, this message translates to:
  /// **'prefix'**
  String get prefix;

  /// No description provided for @distance.
  ///
  /// In en, this message translates to:
  /// **'distance'**
  String get distance;

  /// No description provided for @anyPart.
  ///
  /// In en, this message translates to:
  /// **'any part'**
  String get anyPart;

  /// No description provided for @uiFontSize.
  ///
  /// In en, this message translates to:
  /// **'UI fontSize'**
  String get uiFontSize;

  /// No description provided for @sortBy.
  ///
  /// In en, this message translates to:
  /// **'Sort by: '**
  String get sortBy;

  /// No description provided for @time.
  ///
  /// In en, this message translates to:
  /// **'Time'**
  String get time;

  /// No description provided for @alphabetically.
  ///
  /// In en, this message translates to:
  /// **'Alpha'**
  String get alphabetically;

  /// No description provided for @noHistory.
  ///
  /// In en, this message translates to:
  /// **'no History'**
  String get noHistory;

  /// No description provided for @selectAll.
  ///
  /// In en, this message translates to:
  /// **'Select All'**
  String get selectAll;

  /// No description provided for @selectNone.
  ///
  /// In en, this message translates to:
  /// **'Select None'**
  String get selectNone;

  /// No description provided for @newTabAtEnd.
  ///
  /// In en, this message translates to:
  /// **'New tab at end'**
  String get newTabAtEnd;

  /// No description provided for @searchSuttaName.
  ///
  /// In en, this message translates to:
  /// **'Search Sutta Name'**
  String get searchSuttaName;

  /// No description provided for @nameOrShorthand.
  ///
  /// In en, this message translates to:
  /// **'name or shorthand'**
  String get nameOrShorthand;

  /// No description provided for @fuzzy.
  ///
  /// In en, this message translates to:
  /// **'Fuzzy'**
  String get fuzzy;

  /// No description provided for @notFound.
  ///
  /// In en, this message translates to:
  /// **'Not found'**
  String get notFound;

  /// No description provided for @qjHelpMessage.
  ///
  /// In en, this message translates to:
  /// **'You may search by sutta name or by shorthand sutta notation\n\nExamples:\ndn30 = Dīgha Nikāya 30th sutta\nmn118 = Majjhima Nikāya 118th sutta\nsn5.1 = 5th Saṃyutta first sutta\nan8.64 = book of 8\'s 64th sutta'**
  String get qjHelpMessage;

  /// No description provided for @helpAboutEtc.
  ///
  /// In en, this message translates to:
  /// **'Help, About, Etc.'**
  String get helpAboutEtc;

  /// No description provided for @ok.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// No description provided for @alert.
  ///
  /// In en, this message translates to:
  /// **'Alert'**
  String get alert;

  /// No description provided for @pleaseCloseRestart.
  ///
  /// In en, this message translates to:
  /// **'Please close TPR and launch the app again.'**
  String get pleaseCloseRestart;

  /// No description provided for @resetData.
  ///
  /// In en, this message translates to:
  /// **'Reset Data'**
  String get resetData;

  /// No description provided for @areYouSureReset.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to reset all settings and histories?'**
  String get areYouSureReset;

  /// No description provided for @wordSplit.
  ///
  /// In en, this message translates to:
  /// **'Digital Pāḷi Dictionary'**
  String get wordSplit;

  /// No description provided for @copyingStatus.
  ///
  /// In en, this message translates to:
  /// **'Please wait for initial setup to complete.\nThis may take a few minutes\nIf the status does not change for 60 seconds,\n please hit the reset button and restart.'**
  String get copyingStatus;

  /// No description provided for @about_info.
  ///
  /// In en, this message translates to:
  /// **'We strive to make the best Pāḷi reading app ever made using with Flutter with a SQLite database.  TPR is available in Windows, MacOS, Linux, iOS, and Android. The Digital Pāḷi Dictionary is used for word splits, and ships with the DPD and DPD Grammar.  DPD was created by Ven Bodhirasa as Creative Commons license.  The ​DPD website is here:  https://digitalpalidictionary.github.io/ .  We owe many thanks to this venerable because a good dictionary and splitter makes or breaks a good Pāḷi reader.  His work is ongoing and you can update with the updated extensions.   Most of the TPR code was written by Venerable Pandazza while I did most of the project management with some minor code additions and bug fixes.  Sumbodhi (Bulgaria) is our part time volunteer consultant who does various challenging tasks.  The PEU (Pāḷi English Ultimate) Is a translated version of the abbreviated Pāli Myanmar Abhidhān Dictionary.  This is an ongoing project translated by humans and Google.  There are 200,457 entries with 118,376 translated by humans.  It is quite useful to help you get the meaning of some difficult words not found in any other dictionary.  You can create issues and request features on the github website https://github.com/bksubhuti/tipitaka-pali-reader/issues , The Pāḷi is claimed to be copyright by VRI as cc-by-nc-attrib, The logo uses 3 books which was modified and used with permission by Michael Backman of www.michaelbackmanltd.com .  The Lao Font called LaoPaliRegular.ttf was created and copyrighted by Ven Jayasaro which was modified from a Google Font.  Both are free to use.  Download was from https://drive.google.com/drive/folders/1r-RfuoiMl1YwGk-0PD0g4VsAiRMOf0QG any license info is there.  MD File Icon Attrib https://www.vecteezy.com/free-vector/md'**
  String get about_info;

  /// No description provided for @aboutToCopy.
  ///
  /// In en, this message translates to:
  /// **'About to copy database to your \nlocal Application folder\n Approximate Size (MB): '**
  String get aboutToCopy;

  /// No description provided for @finishedCopying.
  ///
  /// In en, this message translates to:
  /// **'Finished copying'**
  String get finishedCopying;

  /// No description provided for @buildingWordList.
  ///
  /// In en, this message translates to:
  /// **'Building word list'**
  String get buildingWordList;

  /// No description provided for @finishedBuildingWordList.
  ///
  /// In en, this message translates to:
  /// **'Finished building word list'**
  String get finishedBuildingWordList;

  /// No description provided for @finishedBuildingIndexes.
  ///
  /// In en, this message translates to:
  /// **'Finished building indexes'**
  String get finishedBuildingIndexes;

  /// No description provided for @updatingStatus.
  ///
  /// In en, this message translates to:
  /// **'Please wait while updating to complete.\nThis may take a few minutes\nIf the status does not change for 60 seconds,\n please hit the reset button and restart.'**
  String get updatingStatus;

  /// No description provided for @alwaysShowSplitter.
  ///
  /// In en, this message translates to:
  /// **'Always Show Splitter'**
  String get alwaysShowSplitter;

  /// No description provided for @rateThisApp.
  ///
  /// In en, this message translates to:
  /// **'Rate This App'**
  String get rateThisApp;

  /// No description provided for @wouldLikeToRate.
  ///
  /// In en, this message translates to:
  /// **'Would you like to rate this app?'**
  String get wouldLikeToRate;

  /// No description provided for @booksOpened.
  ///
  /// In en, this message translates to:
  /// **'Books Opened'**
  String get booksOpened;

  /// No description provided for @wordsLookedUp.
  ///
  /// In en, this message translates to:
  /// **'Words Looked Up'**
  String get wordsLookedUp;

  /// No description provided for @never.
  ///
  /// In en, this message translates to:
  /// **'Never Show'**
  String get never;

  /// No description provided for @later.
  ///
  /// In en, this message translates to:
  /// **'Later'**
  String get later;

  /// No description provided for @rateAppNow.
  ///
  /// In en, this message translates to:
  /// **'Rate App Now'**
  String get rateAppNow;

  /// No description provided for @folloingExtensions.
  ///
  /// In en, this message translates to:
  /// **'The following extensions were previously installed:'**
  String get folloingExtensions;

  /// No description provided for @wouldYouLikeToInstall.
  ///
  /// In en, this message translates to:
  /// **'Would you like to install extensions?'**
  String get wouldYouLikeToInstall;

  /// No description provided for @multiHighlight.
  ///
  /// In en, this message translates to:
  /// **'Multiple Highlight'**
  String get multiHighlight;

  /// No description provided for @velthuisHelp.
  ///
  /// In en, this message translates to:
  /// **'Velthuis System:\naa=ā, ii=ī uu=ū\n \n.t = ṭ, .d = ḍ\n.n = ṇ, .l = ḷ .m = ṃ\n\"n = ṅ, ~n = ñ'**
  String get velthuisHelp;

  /// No description provided for @turnOnInternet.
  ///
  /// In en, this message translates to:
  /// **'Please turn on the internet'**
  String get turnOnInternet;

  /// No description provided for @updateComplete.
  ///
  /// In en, this message translates to:
  /// **'Update is complete'**
  String get updateComplete;

  /// No description provided for @addingWordlist.
  ///
  /// In en, this message translates to:
  /// **'Adding English wordlist'**
  String get addingWordlist;

  /// No description provided for @englishWordListComplete.
  ///
  /// In en, this message translates to:
  /// **'English wordlist is complete'**
  String get englishWordListComplete;

  /// No description provided for @creatingWordList.
  ///
  /// In en, this message translates to:
  /// **'Creating unique wordlist\n'**
  String get creatingWordList;

  /// No description provided for @deletingRecords.
  ///
  /// In en, this message translates to:
  /// **'\nNow Deleting Records'**
  String get deletingRecords;

  /// No description provided for @insertComplete.
  ///
  /// In en, this message translates to:
  /// **'Insert is complete'**
  String get insertComplete;

  /// No description provided for @ftsIsComplete.
  ///
  /// In en, this message translates to:
  /// **'FTS is complete'**
  String get ftsIsComplete;

  /// No description provided for @reloadingExtensionList.
  ///
  /// In en, this message translates to:
  /// **'Reloading extension list'**
  String get reloadingExtensionList;

  /// No description provided for @rebuildingIndex.
  ///
  /// In en, this message translates to:
  /// **'Rebuilding Index'**
  String get rebuildingIndex;

  /// No description provided for @buildingFts.
  ///
  /// In en, this message translates to:
  /// **'Building fts'**
  String get buildingFts;

  /// No description provided for @whatsNew.
  ///
  /// In en, this message translates to:
  /// **'What\'s New:'**
  String get whatsNew;

  /// No description provided for @showWhatsNew.
  ///
  /// In en, this message translates to:
  /// **'Show What\'s New'**
  String get showWhatsNew;

  /// No description provided for @tools.
  ///
  /// In en, this message translates to:
  /// **'Tools'**
  String get tools;

  /// No description provided for @flashcards.
  ///
  /// In en, this message translates to:
  /// **'Flashcards'**
  String get flashcards;

  /// No description provided for @flashcardSetup.
  ///
  /// In en, this message translates to:
  /// **'Flash Card Setup'**
  String get flashcardSetup;

  /// No description provided for @practiceNow.
  ///
  /// In en, this message translates to:
  /// **'Practice Now'**
  String get practiceNow;

  /// No description provided for @export.
  ///
  /// In en, this message translates to:
  /// **'Export'**
  String get export;

  /// No description provided for @searchSelected.
  ///
  /// In en, this message translates to:
  /// **'Search Selected'**
  String get searchSelected;

  /// No description provided for @searchInCurrent.
  ///
  /// In en, this message translates to:
  /// **'Search in Current'**
  String get searchInCurrent;

  /// No description provided for @upgrade.
  ///
  /// In en, this message translates to:
  /// **'Upgrade'**
  String get upgrade;

  /// No description provided for @persistentSearchFilter.
  ///
  /// In en, this message translates to:
  /// **'Persistent Search Filter'**
  String get persistentSearchFilter;

  /// No description provided for @disableVelthuis.
  ///
  /// In en, this message translates to:
  /// **'Disable Velthuis Input'**
  String get disableVelthuis;

  /// No description provided for @scriptConverter.
  ///
  /// In en, this message translates to:
  /// **'Script Converter'**
  String get scriptConverter;

  /// No description provided for @copy.
  ///
  /// In en, this message translates to:
  /// **'Copy'**
  String get copy;

  /// No description provided for @inputScript.
  ///
  /// In en, this message translates to:
  /// **'Script'**
  String get inputScript;

  /// No description provided for @outputScript.
  ///
  /// In en, this message translates to:
  /// **'Script'**
  String get outputScript;

  /// No description provided for @dictionaryPrevious.
  ///
  /// In en, this message translates to:
  /// **'Previous (Alt + ←)'**
  String get dictionaryPrevious;

  /// No description provided for @dictionaryNext.
  ///
  /// In en, this message translates to:
  /// **'Next (Alt + →)'**
  String get dictionaryNext;

  /// No description provided for @notListed.
  ///
  /// In en, this message translates to:
  /// **'Not Listed'**
  String get notListed;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Processing'**
  String get processing;

  /// No description provided for @fixWordlist.
  ///
  /// In en, this message translates to:
  /// **'Fix Search Suggest Word List'**
  String get fixWordlist;

  /// No description provided for @material3.
  ///
  /// In en, this message translates to:
  /// **'Material 3'**
  String get material3;

  /// No description provided for @color.
  ///
  /// In en, this message translates to:
  /// **'Color'**
  String get color;

  /// No description provided for @importBookmarks.
  ///
  /// In en, this message translates to:
  /// **'Import Bookmarks'**
  String get importBookmarks;

  /// No description provided for @exportBookmarks.
  ///
  /// In en, this message translates to:
  /// **'Export Bookmarks'**
  String get exportBookmarks;

  /// No description provided for @selectRomanFont.
  ///
  /// In en, this message translates to:
  /// **'Select Roman Font'**
  String get selectRomanFont;

  /// No description provided for @transferBookmarks.
  ///
  /// In en, this message translates to:
  /// **'Transfer Bookmarks'**
  String get transferBookmarks;

  /// No description provided for @cloudBookmarks.
  ///
  /// In en, this message translates to:
  /// **'Cloud Bookmarks'**
  String get cloudBookmarks;

  /// No description provided for @localBookmarks.
  ///
  /// In en, this message translates to:
  /// **'Local Bookmarks'**
  String get localBookmarks;

  /// No description provided for @cloudSettings.
  ///
  /// In en, this message translates to:
  /// **'Cloud Settings'**
  String get cloudSettings;

  /// No description provided for @resetPassword.
  ///
  /// In en, this message translates to:
  /// **'Request Password Reset'**
  String get resetPassword;

  /// No description provided for @register.
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get register;

  /// No description provided for @signIn.
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signIn;

  /// No description provided for @signOut.
  ///
  /// In en, this message translates to:
  /// **'Sign Out'**
  String get signOut;

  /// No description provided for @email.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get email;

  /// No description provided for @password.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get password;

  /// No description provided for @submit.
  ///
  /// In en, this message translates to:
  /// **'Submit'**
  String get submit;

  /// No description provided for @savePassword.
  ///
  /// In en, this message translates to:
  /// **'Save Password'**
  String get savePassword;

  /// No description provided for @savePasswordMessage.
  ///
  /// In en, this message translates to:
  /// **'Would you like to save this password for future logins?'**
  String get savePasswordMessage;

  /// No description provided for @resetPasswordMessage.
  ///
  /// In en, this message translates to:
  /// **'Enter your email address to recieve a password reset email'**
  String get resetPasswordMessage;

  /// No description provided for @passwordTooShort.
  ///
  /// In en, this message translates to:
  /// **'Password must be at least 8 characters'**
  String get passwordTooShort;

  /// No description provided for @loginFailed.
  ///
  /// In en, this message translates to:
  /// **'loginFailed'**
  String get loginFailed;

  /// No description provided for @registrationSuccessful.
  ///
  /// In en, this message translates to:
  /// **'Regisetration was successful.\nCheck your email or spam folder to verify.\nThen please sign in.'**
  String get registrationSuccessful;

  /// No description provided for @registrationFailed.
  ///
  /// In en, this message translates to:
  /// **'Registration failed'**
  String get registrationFailed;

  /// No description provided for @loginSuccess.
  ///
  /// In en, this message translates to:
  /// **'Login Successful'**
  String get loginSuccess;

  /// No description provided for @verificationNeeded.
  ///
  /// In en, this message translates to:
  /// **'Email verification needed.\nCheck email or spam folder\nSign in again to resend'**
  String get verificationNeeded;

  /// No description provided for @enterPassword.
  ///
  /// In en, this message translates to:
  /// **'Please enter your password'**
  String get enterPassword;

  /// No description provided for @enterEmail.
  ///
  /// In en, this message translates to:
  /// **'Please enter your email'**
  String get enterEmail;

  /// No description provided for @enterValidEmail.
  ///
  /// In en, this message translates to:
  /// **'Please enter a valid email'**
  String get enterValidEmail;

  /// No description provided for @folder.
  ///
  /// In en, this message translates to:
  /// **'Folder'**
  String get folder;

  /// No description provided for @edit.
  ///
  /// In en, this message translates to:
  /// **'Edit'**
  String get edit;

  /// No description provided for @moveToFolder.
  ///
  /// In en, this message translates to:
  /// **'Move To Folder'**
  String get moveToFolder;

  /// No description provided for @enterNewNote.
  ///
  /// In en, this message translates to:
  /// **'Enter new note'**
  String get enterNewNote;

  /// No description provided for @editBookmarkNote.
  ///
  /// In en, this message translates to:
  /// **'Edit Bookmark Note'**
  String get editBookmarkNote;

  /// No description provided for @editFolderName.
  ///
  /// In en, this message translates to:
  /// **'Edit Folder Name'**
  String get editFolderName;

  /// No description provided for @enterNewFolderName.
  ///
  /// In en, this message translates to:
  /// **'Enter new folder name'**
  String get enterNewFolderName;

  /// No description provided for @newFolder.
  ///
  /// In en, this message translates to:
  /// **'New Folder'**
  String get newFolder;

  /// No description provided for @folderName.
  ///
  /// In en, this message translates to:
  /// **'Folder Name'**
  String get folderName;

  /// No description provided for @create.
  ///
  /// In en, this message translates to:
  /// **'Create'**
  String get create;

  /// No description provided for @createNewFolder.
  ///
  /// In en, this message translates to:
  /// **'Create New Folder'**
  String get createNewFolder;

  /// No description provided for @confirmDelete.
  ///
  /// In en, this message translates to:
  /// **'Confirm Delete'**
  String get confirmDelete;

  /// No description provided for @areYouSureDelete.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete this item?'**
  String get areYouSureDelete;

  /// No description provided for @hidescrollbars.
  ///
  /// In en, this message translates to:
  /// **'Hide Scrollbars'**
  String get hidescrollbars;

  /// No description provided for @dpdSettings.
  ///
  /// In en, this message translates to:
  /// **'DPD Settings'**
  String get dpdSettings;

  /// No description provided for @hideIPA.
  ///
  /// In en, this message translates to:
  /// **'Hide IPA'**
  String get hideIPA;

  /// No description provided for @hideSanskrit.
  ///
  /// In en, this message translates to:
  /// **'Hide Sanskrit'**
  String get hideSanskrit;

  /// No description provided for @inflectionNoDataTitle.
  ///
  /// In en, this message translates to:
  /// **'Inflection Not Found'**
  String get inflectionNoDataTitle;

  /// No description provided for @inflectionNoDataMessage.
  ///
  /// In en, this message translates to:
  /// **'Selected word has no data.'**
  String get inflectionNoDataMessage;

  /// No description provided for @checkingInternet.
  ///
  /// In en, this message translates to:
  /// **'Checking Internet connection'**
  String get checkingInternet;

  /// No description provided for @aiSettings.
  ///
  /// In en, this message translates to:
  /// **'AI Settings'**
  String get aiSettings;

  /// No description provided for @openRouterAiModel.
  ///
  /// In en, this message translates to:
  /// **'OpenRouter Model'**
  String get openRouterAiModel;

  /// No description provided for @openRouterAiKey.
  ///
  /// In en, this message translates to:
  /// **'OpenRouter key'**
  String get openRouterAiKey;

  /// No description provided for @key.
  ///
  /// In en, this message translates to:
  /// **'key?'**
  String get key;

  /// No description provided for @updateModelList.
  ///
  /// In en, this message translates to:
  /// **'Update Model List'**
  String get updateModelList;

  /// No description provided for @customAiPromptLabel.
  ///
  /// In en, this message translates to:
  /// **'Custom AI Prompt'**
  String get customAiPromptLabel;

  /// No description provided for @chooseAiPrompt.
  ///
  /// In en, this message translates to:
  /// **'Choose a canned AI prompt'**
  String get chooseAiPrompt;

  /// No description provided for @translatePaliLineByLine.
  ///
  /// In en, this message translates to:
  /// **'Translate line by line'**
  String get translatePaliLineByLine;

  /// No description provided for @translatePali.
  ///
  /// In en, this message translates to:
  /// **'Translate the Pāḷi'**
  String get translatePali;

  /// No description provided for @explainGrammar.
  ///
  /// In en, this message translates to:
  /// **'Explain grammar'**
  String get explainGrammar;

  /// No description provided for @summarize.
  ///
  /// In en, this message translates to:
  /// **'Summarize passage'**
  String get summarize;

  /// No description provided for @translatePaliLineByLinePrompt.
  ///
  /// In en, this message translates to:
  /// **'Translate the following Pāḷi into clean, readable HTML. Translate sentence by sentence Pali and English Languages. Use <b> for Pāḷi line and <br> to separate lines. Normal text for English. Do not translate common terms like Nibbāna, mettā, or dukkha. Output only HTML. Do not explain.  Use original script for pali as given'**
  String get translatePaliLineByLinePrompt;

  /// No description provided for @translatePaliPrompt.
  ///
  /// In en, this message translates to:
  /// **'Translate the following Pāḷi into English Langauge.  Make clean, readable HTML.  Do not translate common terms like Nibbāna, mettā, or dukkha. Output only HTML. Do not explain.'**
  String get translatePaliPrompt;

  /// No description provided for @explainGrammarPrompt.
  ///
  /// In en, this message translates to:
  /// **'Explain the grammar of the following Pāḷi passage in simple English language. Focus on roots, compounds, taddhita, and samāsa if present. Be brief. Output in formatted HTML. Do not translate the Pāḷi.  Use original script for pali as given'**
  String get explainGrammarPrompt;

  /// No description provided for @summarizePrompt.
  ///
  /// In en, this message translates to:
  /// **'Summarize the following Pāḷi passage in one or two English Language sentences. Focus on the key ideas. Output plain text. Do not translate unless necessary.'**
  String get summarizePrompt;

  /// No description provided for @resetAiPromptDefault.
  ///
  /// In en, this message translates to:
  /// **'Reset to Default'**
  String get resetAiPromptDefault;

  /// No description provided for @aiContext.
  ///
  /// In en, this message translates to:
  /// **'AI Context'**
  String get aiContext;

  /// No description provided for @usingAI.
  ///
  /// In en, this message translates to:
  /// **'Using AI...'**
  String get usingAI;

  /// No description provided for @openRouterKeySaved.
  ///
  /// In en, this message translates to:
  /// **'API Key saved'**
  String get openRouterKeySaved;

  /// No description provided for @howToGetApiKey.
  ///
  /// In en, this message translates to:
  /// **'How to Get an OpenRouter API Key'**
  String get howToGetApiKey;

  /// No description provided for @apiKeyInstructions1.
  ///
  /// In en, this message translates to:
  /// **'To use AI translation, you need a free API key from OpenRouter.ai.'**
  String get apiKeyInstructions1;

  /// No description provided for @apiKeyInstructions2.
  ///
  /// In en, this message translates to:
  /// **'• Visit the OpenRouter website and sign up for an account.'**
  String get apiKeyInstructions2;

  /// No description provided for @apiKeyInstructions3.
  ///
  /// In en, this message translates to:
  /// **'• Once logged in, you can get your API key.'**
  String get apiKeyInstructions3;

  /// No description provided for @apiKeyInstructions4.
  ///
  /// In en, this message translates to:
  /// **'💡 Models with a dollar sign require payment.'**
  String get apiKeyInstructions4;

  /// No description provided for @apiKeyInstructions5.
  ///
  /// In en, this message translates to:
  /// **'• The number of dollar signs roughly shows the relative cost which are not much per request.'**
  String get apiKeyInstructions5;

  /// No description provided for @apiKeyInstructions6.
  ///
  /// In en, this message translates to:
  /// **'• Please see OpenRouter for current costs and estimates.'**
  String get apiKeyInstructions6;

  /// No description provided for @apiKeyInstructions7.
  ///
  /// In en, this message translates to:
  /// **'Use free models like Gemini Flash, DeepSeek, etc.'**
  String get apiKeyInstructions7;

  /// No description provided for @getOpenRouterKey.
  ///
  /// In en, this message translates to:
  /// **'Get Openrouter Key'**
  String get getOpenRouterKey;

  /// No description provided for @getGenminiKey.
  ///
  /// In en, this message translates to:
  /// **'Get Gemini Key'**
  String get getGenminiKey;

  /// No description provided for @hide.
  ///
  /// In en, this message translates to:
  /// **'Hide'**
  String get hide;

  /// No description provided for @aiTranslationTitle.
  ///
  /// In en, this message translates to:
  /// **'AI Translation'**
  String get aiTranslationTitle;

  /// No description provided for @noTextSelected.
  ///
  /// In en, this message translates to:
  /// **'No text selected for translation.'**
  String get noTextSelected;

  /// No description provided for @aiWarning.
  ///
  /// In en, this message translates to:
  /// **'⚠️ This translation was generated by an AI model. Accuracy is not guaranteed.'**
  String get aiWarning;

  /// No description provided for @aiTruncationNote.
  ///
  /// In en, this message translates to:
  /// **'Note: Only the first 1000 characters were sent for translation.'**
  String get aiTruncationNote;

  /// No description provided for @noTranslationReturned.
  ///
  /// In en, this message translates to:
  /// **'No translation returned.'**
  String get noTranslationReturned;

  /// No description provided for @errorOccurred.
  ///
  /// In en, this message translates to:
  /// **'An error occurred.'**
  String get errorOccurred;

  /// Exception message shown if OpenRouter fails
  ///
  /// In en, this message translates to:
  /// **'Exception: {error}'**
  String exceptionMessage(Object error);

  /// No description provided for @shareSubject.
  ///
  /// In en, this message translates to:
  /// **'Pāḷi text from TPR'**
  String get shareSubject;

  /// No description provided for @importEpub.
  ///
  /// In en, this message translates to:
  /// **'Import EPUB Book'**
  String get importEpub;

  /// No description provided for @selectAnEpubFileToImport.
  ///
  /// In en, this message translates to:
  /// **'Select an EPUB file to import into TPR.'**
  String get selectAnEpubFileToImport;

  /// No description provided for @selectFile.
  ///
  /// In en, this message translates to:
  /// **'Select File'**
  String get selectFile;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>['bn', 'ccp', 'en', 'hi', 'it', 'km', 'lo', 'my', 'ru', 'si', 'th', 'vi', 'zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {


  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'bn': return AppLocalizationsBn();
    case 'ccp': return AppLocalizationsCcp();
    case 'en': return AppLocalizationsEn();
    case 'hi': return AppLocalizationsHi();
    case 'it': return AppLocalizationsIt();
    case 'km': return AppLocalizationsKm();
    case 'lo': return AppLocalizationsLo();
    case 'my': return AppLocalizationsMy();
    case 'ru': return AppLocalizationsRu();
    case 'si': return AppLocalizationsSi();
    case 'th': return AppLocalizationsTh();
    case 'vi': return AppLocalizationsVi();
    case 'zh': return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.'
  );
}
