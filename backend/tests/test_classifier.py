#!/usr/bin/env python3
"""Quick test for the clinical classifier"""

from app.models.classifier import classifier
import sys

print('='*70)
print('CLINICAL CLASSIFIER TEST')
print('='*70)

# Load model
print('\nLoading model...')
classifier.load()
print(f'Model loaded: {classifier.is_loaded}')
print(f'Classes: {list(classifier._classes)}')

# Test cases
test_cases = [
    ('I feel happy today', 'Normal'),
    ('I want to end my life', 'Suicidal'),
    ('I feel hopeless and empty', 'Depression'),
    ('My heart races with anxiety', 'Anxiety'),
    ('Work is overwhelming', 'Stress'),
    ('I have extreme mood swings', 'Bipolar'),
    ('I feel disconnected from myself', 'Personality disorder'),
    ('', 'Unknown'),
]

print('\n' + '='*70)
print('TEST RESULTS')
print('='*70)

correct = 0
total = len(test_cases)

for text, expected in test_cases:
    result = classifier.predict(text)
    predicted = result['category']
    confidence = result['confidence']
    is_correct = predicted == expected
    if is_correct:
        correct += 1
    status = '[OK]' if is_correct else '[FAIL]'
    display_text = text[:40] + '...' if len(text) > 40 else text
    print(f'{status} "{display_text}" -> {predicted} ({confidence:.2%}) [expected: {expected}]')

print(f'\nAccuracy: {correct}/{total} ({correct/total:.0%})')

# Edge cases
print('\n' + '='*70)
print('EDGE CASES')
print('='*70)

edge_cases = [
    ('I am not suicidal, just stressed', 'Should not be Suicidal'),
    ('suicide', 'Should detect crisis term'),
    ('!!!???', 'Should be Unknown'),
    ('12345', 'Should be Unknown'),
]

for text, note in edge_cases:
    result = classifier.predict(text)
    display_text = text[:30] + '...' if len(text) > 30 else text
    print(f'"{display_text}" -> {result["category"]} ({result["confidence"]:.2%}) - {note}')

if __name__ == "__main__":
    print('\n[OK] Tests completed successfully!')
