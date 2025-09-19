import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert'; // for encoding/decoding JSON

void main() {
  runApp(const JournalApp());
}

/// Root widget of the app
class JournalApp extends StatelessWidget {
  const JournalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My Journal',
      theme: ThemeData(primarySwatch: Colors.deepPurple),
      home: const JournalHome(),
    );
  }
}

/// Data model for a journal entry
/// Each entry has:
/// - text content
/// - timestamp (when it was written/edited)
class JournalEntry {
  final String text;
  final String timestamp;

  JournalEntry({required this.text, required this.timestamp});

  // Convert JournalEntry -> Map (for saving as JSON)
  Map<String, String> toMap() {
    return {
      'text': text,
      'timestamp': timestamp,
    };
  }

  // Convert Map -> JournalEntry (for restoring from JSON)
  factory JournalEntry.fromMap(Map<String, dynamic> map) {
    return JournalEntry(
      text: map['text'] ?? '',
      timestamp: map['timestamp'] ?? '',
    );
  }
}

class JournalHome extends StatefulWidget {
  const JournalHome({super.key});

  @override
  State<JournalHome> createState() => _JournalHomeState();
}

class _JournalHomeState extends State<JournalHome> {
  List<JournalEntry> _entries = [];

  @override
  void initState() {
    super.initState();
    _loadEntries();
  }

  /// Load saved entries from SharedPreferences
  Future<void> _loadEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> stored = prefs.getStringList('journal_entries') ?? [];

    setState(() {
      _entries =
          stored.map((jsonStr) => JournalEntry.fromMap(jsonDecode(jsonStr))).toList();
    });
  }

  /// Save all entries back to SharedPreferences
  Future<void> _saveEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final encoded = _entries.map((e) => jsonEncode(e.toMap())).toList();
    await prefs.setStringList('journal_entries', encoded);
  }

  /// Add a new entry
  Future<void> _addEntry(String text) async {
    final now = DateTime.now();
    final formatted =
        "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} "
        "${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}";

    setState(() {
      _entries.add(JournalEntry(text: text, timestamp: formatted));
    });
    await _saveEntries();
  }

  /// Edit an existing entry (replace at index)
  Future<void> _editEntry(int index, String newText) async {
    final now = DateTime.now();
    final formatted =
        "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} "
        "${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}";

    setState(() {
      _entries[index] = JournalEntry(text: newText, timestamp: formatted);
    });
    await _saveEntries();
  }

  /// Delete an entry
  Future<void> _deleteEntry(int index) async {
    setState(() {
      _entries.removeAt(index);
    });
    await _saveEntries();
  }

  /// Show a dialog to add or edit an entry
  void _showEntryDialog({int? editIndex}) {
    final controller = TextEditingController();

    // If editing, pre-fill text field with current entry
    if (editIndex != null) {
      controller.text = _entries[editIndex].text;
    }

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(editIndex == null ? 'New Journal Entry' : 'Edit Journal Entry'),
        content: TextField(
          controller: controller,
          maxLines: 5,
          decoration: const InputDecoration(hintText: "Write your thoughts..."),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context), // Cancel
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () {
              final text = controller.text.trim();
              if (text.isNotEmpty) {
                if (editIndex == null) {
                  _addEntry(text); // Add new entry
                } else {
                  _editEntry(editIndex, text); // Edit existing
                }
              }
              Navigator.pop(context); // Close dialog
            },
            child: const Text("Save"),
          ),
        ],
      ),
    );
  }

  /// Build the journal list UI
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Journal')),
      body: _entries.isEmpty
          ? const Center(child: Text("No journal entries yet."))
          : ListView.builder(
        itemCount: _entries.length,
        itemBuilder: (context, index) {
          final entry = _entries[index];
          return Card(
            margin: const EdgeInsets.all(8),
            child: ListTile(
              title: Text(entry.text),
              subtitle: Text("Last edited: ${entry.timestamp}"),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit, color: Colors.blue),
                    onPressed: () => _showEntryDialog(editIndex: index),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _deleteEntry(index),
                  ),
                ],
              ),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showEntryDialog(), // Add new entry
        child: const Icon(Icons.add),
      ),
    );
  }
}
