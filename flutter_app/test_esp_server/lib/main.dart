import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BlindViz -  2.0',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'BlindViz - 2.0'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  bool _isListening = false;
  String _speechText = "Press the button and start speaking";

  @override
  void initState() {
    super.initState();
    print("Initializing Speech-to-Text...");
    _initializeSpeechToText();
  }

  void _initializeSpeechToText() async {
    var status = await Permission.microphone.request();
    if (status.isGranted) {
      bool available = await _speech.initialize();
      if (available) {
        print("Speech-to-Text initialized.");
      } else {
        print("Speech-to-Text not available.");
      }
    } else {
      print("Microphone permission not granted.");
    }
  }

  Future<void> _startListening() async {
    if (_isListening) {
      // Stop listening if already active
      await _speech.stop();
      setState(() => _isListening = false);
    }

    // Start listening
    bool available = await _speech.initialize();
    if (available) {
      setState(() => _isListening = true);
      _speech.listen(onResult: (result) async {
        setState(() {
          _speechText = result.recognizedWords;
        });

        // If STT stops listening, process the speech
        if (!_speech.isListening) {
          await _processSpeech(_speechText);
          setState(() => _isListening = false); // Reset the listening state
        }
      });
    } else {
      print("Speech-to-Text not available.");
      setState(() => _isListening = false);
    }
  }

  Future<void> _stopListening() async {
    await _speech.stop();
    setState(() => _isListening = false);
  }

  Future<void> _processSpeech(String speechText) async {
    String url;
    bool isAnalyze = speechText.toLowerCase().contains("analyse");

    if (isAnalyze) {
      url = "http://192.168.248.3:80/capture";
    } else {
      url = "";
    }

    try {
      if (isAnalyze) {
        // Send a GET request if "analyze" is found
        print("Sending GET request");
        final response = await http.get(Uri.parse(url));
        if (response.statusCode == 200) {
          await _speak(response.body);
        } else {
          await _speak("Error: Unable to process the GET request.");
        }
      } else {
        // Send a POST request otherwise
        final response =
            await http.post(Uri.parse(url), body: {'text': speechText});
        if (response.statusCode == 200) {
          await _speak(response.body);
        } else {
          await _speak("Error: Unable to process the POST request.");
        }
      }
    } catch (e) {
      print(e);
      await _speak("Error: Something went wrong.");
    } finally {
      // Ensure the listening state is reset after processing
      setState(() => _isListening = false);
    }
  }

  Future<void> _speak(String text) async {
    await _flutterTts.speak(text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              _speechText,
              style: Theme.of(context).textTheme.headlineMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _isListening ? _stopListening : _startListening,
        tooltip: _isListening ? 'Stop Listening' : 'Start Listening',
        child: Icon(_isListening ? Icons.mic_off : Icons.mic),
      ),
    );
  }
}
