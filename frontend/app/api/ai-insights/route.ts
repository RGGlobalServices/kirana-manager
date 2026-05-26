import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { generateSmartInsights, type Product } from '@/lib/smartInsights';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { products, summary, district, locale } = body as {
    products: Product[];
    summary: any;
    district: string;
    locale: string;
  };

  // ── Try NVIDIA AI first ──────────────────────────────────────────
  const apiKey = process.env.NVIDIA_API_KEY;
  if (apiKey && apiKey.trim() !== '') {
    try {
      const ai = new OpenAI({
        baseURL: "https://integrate.api.nvidia.com/v1",
        apiKey: apiKey
      });
      const langLabel = locale === 'hi' ? 'Hindi' : locale === 'mr' ? 'Marathi' : 'English';

      const prompt = `You are an AI market analyst for a Kirana (Indian grocery) store in ${district || 'Pune'} district, Maharashtra, India.
      
      TASK 1: Perform a REAL-TIME search for the current wholesale and retail prices of major grocery items (Sugar, Cooking Oil, Rice, Flour, Wheat, Dals) specifically in the ${district} district of Maharashtra.
      TASK 2: Analyze the store inventory provided below.
      TASK 3: Provide price recommendations based on REAL MARKET DATA found in Task 1.

${products && products.length > 0 ? `
Store inventory data:
${JSON.stringify(products.slice(0, 50), null, 2)}
` : 'Store inventory is currently empty.'}

Yesterday's summary:
- Total Sales: Rs.${summary?.sales || 0}
- Total Cost: Rs.${summary?.cost || 0}
- Gross Profit: Rs.${summary?.profit || 0}
- Total Transactions: ${summary?.transactions || 0}
- Top selling: ${summary?.top_selling?.map((s: any) => `${s.name} (${s.qty} units)`).join(', ') || 'None'}

Respond ONLY with a valid JSON object (no markdown, no code fences, no extra text) with this structure:
{
  "priceRecommendations": [
    { "product": "name", "currentPrice": 0, "marketPrice": 0, "suggestion": "text in ${langLabel}", "trend": "up" }
  ],
  "stockAlerts": [
    { "product": "name", "stock": 0, "minStock": 0, "urgency": "critical", "message": "text in ${langLabel}" }
  ],
  "profitAnalysis": {
    "yesterday": {
      "sales": ${summary?.sales || 0}, "cost": ${summary?.cost || 0}, "profit": ${summary?.profit || 0}, "profitMargin": ${summary?.sales > 0 ? (summary.profit/summary.sales)*100 : 0},
      "status": "${(summary?.profit || 0) >= 0 ? 'profit' : 'loss'}", "summary": "text in ${langLabel}"
    }
  },
  "suggestions": [
    { "title": "title in ${langLabel}", "detail": "detail in ${langLabel}", "impact": "high", "category": "pricing" }
  ]
}
Rules: 
- For "marketPrice", use the ACTUAL current price found via search for ${district} or nearest Maharashtra hub.
- trend = "up"|"down"|"stable", urgency = "critical"|"low"|"order_soon", impact = "high"|"medium"|"low", category = "pricing"|"stock"|"marketing"|"operations".
- Use realistic Maharashtra ${district} district market prices. Give 3-4 price recs, all low/zero stock alerts, 4 suggestions.`;

      const result = await ai.chat.completions.create({
        model: 'meta/llama-3.1-8b-instruct',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2048,
        temperature: 0.2,
      });
      
      const text = result.choices[0].message.content ?? '';
      const clean = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```\s*$/i, '').trim();
      const data  = JSON.parse(clean);
      return NextResponse.json({ ...data, source: 'ai' });

    } catch (aiErr) {
      // AI failed — log and fall through to smart engine
      console.warn('NVIDIA AI unavailable, using smart insights:', aiErr instanceof Error ? aiErr.message : aiErr);
    }
  }

  // ── Smart local fallback (zero cost) ────────────────────────────
  const smartData = generateSmartInsights(products, district, locale, summary);
  return NextResponse.json(smartData);
}
