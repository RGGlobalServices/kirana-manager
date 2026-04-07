import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json([
    {id: 1, name: "Fortune तेल (1L)", category: "Oil", stock: 45, minStock: 10, mrp: 180, sellingPrice: 170, cost: 155, barcode: "8901234567890"},
    {id: 2, name: "तूर डाळ (1kg)", category: "Pulses", stock: 4, minStock: 5, mrp: 160, sellingPrice: 150, cost: 135, barcode: "8901234567891"},
    {id: 3, name: "साखर (1kg)", category: "Sugar", stock: 120, minStock: 20, mrp: 45, sellingPrice: 42, cost: 38, barcode: "8901234567893"},
    {id: 4, name: "Surf Excel (500g)", category: "Detergent", stock: 8, minStock: 10, mrp: 120, sellingPrice: 115, cost: 100, barcode: "8901234567894"},
  ]);
}
