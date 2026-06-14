import 'package:flutter/material.dart';

void main() {
  runApp(const TravelMarketplaceApp());
}

class TravelMarketplaceApp extends StatelessWidget {
  const TravelMarketplaceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Consumer Travel Marketplace',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF005EA8)),
        useMaterial3: true,
      ),
      home: const MarketplaceHomePage(),
    );
  }
}

class MarketplaceHomePage extends StatelessWidget {
  const MarketplaceHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Consumer Travel Marketplace')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Semantics(
                    header: true,
                    child: Text(
                      'Plan personal, business, and group travel',
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'This development shell is ready for secure Firebase '
                    'Authentication, Amadeus search, provider-neutral checkout, '
                    'and accessible trip management.',
                  ),
                  const SizedBox(height: 24),
                  const Card(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Text(
                        'Demonstration mode: no reservations or payments are '
                        'made. Firebase project identifiers and credentials are '
                        'not embedded in this build.',
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
