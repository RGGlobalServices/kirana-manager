import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json([
    {id: 1, name: "Rahul Gosavi", mobile: "9876543210", due: 1250, lastPayment: "2 days ago"},
    {id: 2, name: "Suresh Patil", mobile: "9123456789", due: 4500, lastPayment: "1 week ago"},
  ]);
}
