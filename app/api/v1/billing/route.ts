import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json({
    id: Math.floor(Math.random() * 1000),
    total_amount: 170,
    total_profit: 15,
    created_at: new Date().toISOString()
  });
}
