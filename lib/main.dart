import 'package:flutter/material.dart';

void main() {
  runApp(const LoveLoveApp());
}

class LoveLoveApp extends StatelessWidget {
  const LoveLoveApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LoveLove',
      theme: ThemeData(
        primarySwatch: Colors.pink,
      ),
      home: const JournalScreen(),
    );
  }
}

class JournalScreen extends StatelessWidget {
  const JournalScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("LoveLove Journal")),
      body: const Center(
        child: Text(
          "Welcome to LoveLove 💖\nStart your first journal entry!",
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 18),
        ),
      ),
    );
  }
}
