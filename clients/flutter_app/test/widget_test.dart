import 'package:flutter_test/flutter_test.dart';
import 'package:travel_marketplace/main.dart';

void main() {
  testWidgets('discloses demonstration mode', (tester) async {
    await tester.pumpWidget(const TravelMarketplaceApp());

    expect(find.textContaining('Plan personal'), findsOneWidget);
    expect(find.textContaining('Demonstration mode'), findsOneWidget);
  });
}
