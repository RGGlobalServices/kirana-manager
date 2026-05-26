import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    today_sales: 6800,
    today_profit: 1250,
    total_udhar: 12450,
    low_stock_count: 8
  });
}
