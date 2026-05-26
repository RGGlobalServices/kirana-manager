import { translateData } from '../frontend/lib/translateData';

const testCases = [
    { text: 'Fortune Oil', locale: 'hi', expected: 'Fortune तेल' },
    { text: 'Fortune Oil', locale: 'mr', expected: 'Fortune तेल' },
    { text: 'Ltr', locale: 'mr', expected: 'लिटर' },
    { text: 'Soap', locale: 'mr', expected: 'साबण' }
];

testCases.forEach(c => {
    const result = translateData(c.text, c.locale);
    console.log(`[${c.locale}] "${c.text}" -> "${result}" (Expected: "${c.expected}")`);
});
