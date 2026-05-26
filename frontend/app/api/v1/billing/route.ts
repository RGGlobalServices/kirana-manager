import { NextRequest, NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8000';

export async function GET(req: NextRequest) {
  const url = `${BACKEND}/api/v1/billing${req.nextUrl.search}`;
  const res = await fetch(url, { headers: forwardHeaders(req) });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}

export async function POST(req: NextRequest) {
  const body = await req.text();
  const res = await fetch(`${BACKEND}/api/v1/billing`, {
    method: 'POST',
    headers: { ...forwardHeaders(req), 'content-type': 'application/json' },
    body,
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}

function forwardHeaders(req: NextRequest): Record<string, string> {
  const headers: Record<string, string> = {};
  const auth = req.headers.get('authorization');
  if (auth) headers['authorization'] = auth;
  return headers;
}
