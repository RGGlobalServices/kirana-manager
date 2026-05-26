import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

export async function POST(req: NextRequest) {
  try {
    const { text, targetLocale } = await req.json();

    if (!text || !targetLocale) {
      return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
    }

    if (targetLocale === 'en') return NextResponse.json({ translated: text });

    const apiKey = process.env.NVIDIA_API_KEY;
    if (!apiKey || apiKey.trim() === '') {
      return NextResponse.json({ error: 'NVIDIA API key not configured' }, { status: 500 });
    }

    const ai = new OpenAI({
      baseURL: "https://integrate.api.nvidia.com/v1",
      apiKey: apiKey
    });

    const prompt = `Translate the following Kirana (grocery) product name or category into ${targetLocale === 'mr' ? 'Marathi' : 'Hindi'}.
    Provide ONLY the translated text, no explanation.

    Text: ${text}`;

    const result = await ai.chat.completions.create({
      model: 'meta/llama-3.1-8b-instruct',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 100,
    });
    
    const translated = (result.choices[0].message.content ?? '').trim();

    return NextResponse.json({ translated });
  } catch (err) {
    console.error('AI Translation error:', err);
    return NextResponse.json({ error: 'Translation failed' }, { status: 500 });
  }
}
