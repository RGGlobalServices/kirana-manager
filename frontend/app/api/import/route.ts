import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
const pdfParse = require('pdf-parse');
import * as XLSX from 'xlsx';

const SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'];
const SUPPORTED_DOC_TYPES   = ['application/pdf'];
const SUPPORTED_EXCEL_TYPES = [
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/csv',
];

function detectFileType(mimeType: string): 'image' | 'excel' | 'pdf' | 'other' {
  if (SUPPORTED_IMAGE_TYPES.includes(mimeType)) return 'image';
  if (SUPPORTED_EXCEL_TYPES.includes(mimeType))  return 'excel';
  if (SUPPORTED_DOC_TYPES.includes(mimeType))    return 'pdf';
  return 'other';
}

const PROMPT = `You are the "Vyapar Sarthi AI Agent" for an Indian Kirana (grocery) store.

Your mission is to intelligently analyze various business documents (handwritten ledger photos, invoices, wholesale bills, spreadsheets) and convert them into organized digital data for the stock and khata management system.

Document Types you may encounter:
- "Udhar Khata" or "Ledger": Lists of customer names and balances.
- "Stock Register" or "Invoices": Lists of items purchased/bought with quantities and prices.
- "Cash Memos": Daily sales records.
- "Loan Agreements": Detailed loan notes.

Your Response Mode:
- Be highly precise with numbers and names.
- Handle spelling mistakes intelligently (e.g., if you see "Santuor", know it is likely "Santoor").
- For product units, prefer standard types: Kg, Gram, Bottle, Box, Unit, Liter, Packet.

Respond ONLY with a valid JSON object:
{
  "dataType": "khata" | "stock" | "sales" | "loans" | "mixed",
  "summary": "Proactive summary of the document (e.g., 'Digitized 5 new stock arrivals and matched 3 customer payments.')",
  "rawText": "Verbatim text extracted from document",
  "khata": [
    { "customerName": "string", "amount": 0, "date": "YYYY-MM-DD", "note": "string" }
  ],
  "stock": [
    { "productName": "string", "quantity": 0, "unit": "Kg|Gram|Bottle|Box|Unit|Liter|Packet", "price": 0 }
  ],
  "sales": [
    { "date": "YYYY-MM-DD", "totalAmount": 0, "paymentMethod": "Cash|UPI|Udhar", "note": "string" }
  ],
  "loans": [
    { "lenderName": "string", "amount": 0, "date": "YYYY-MM-DD", "note": "string" }
  ]
}

If you cannot identify a field, omit it from the nested object or use an empty array [].
Respond only with the JSON data.`;

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    const fileType = detectFileType(file.type);
    const buffer   = await file.arrayBuffer();
    const base64   = Buffer.from(buffer).toString('base64');

    const apiKey = process.env.NVIDIA_API_KEY;
    if (!apiKey || apiKey.trim() === '') {
      // Return a mock result if no API key is configured
      return NextResponse.json({
        dataType: 'unknown',
        summary: 'NVIDIA API key not configured — please add it to .env.local',
        rawText: '',
        khata: [],
        stock: [],
        sales: [],
        fileType,
      });
    }

    const ai = new OpenAI({
      baseURL: "https://integrate.api.nvidia.com/v1",
      apiKey: apiKey
    });

    let messages: any[] = [];
    let modelToUse = 'meta/llama-3.2-11b-vision-instruct';

    if (fileType === 'pdf') {
      try {
        let pdfParseFn = pdfParse;
        if (typeof pdfParse !== 'function') {
          pdfParseFn = pdfParse.default || pdfParse.PDFParse;
        }
        
        let extractedText = '';
        try {
          const pdfData = await pdfParseFn(Buffer.from(buffer));
          extractedText = pdfData.text;
        } catch (parseError: any) {
          // If the PDF is corrupted (e.g., bad XRef entry) it might actually be an image renamed to .pdf
          console.warn("PDF parse failed, falling back to Vision model:", parseError.message);
          messages = [
            {
              role: "user",
              content: [
                { type: "text", text: PROMPT },
                {
                  type: "image_url",
                  image_url: { url: `data:image/jpeg;base64,${base64}` }
                }
              ]
            }
          ];
          modelToUse = 'meta/llama-3.2-11b-vision-instruct';
          extractedText = 'fallback-to-image'; // prevent empty text error
        }
        
        if (extractedText !== 'fallback-to-image') {
          if (!extractedText || extractedText.trim().length === 0) {
            throw new Error("No readable text found in PDF. If this is a scanned document, please convert or upload it as an Image (JPG/PNG) so the Vision AI can read it.");
          }

          messages = [
            {
              role: "user",
              content: `${PROMPT}\n\nHere is the extracted text from the PDF document:\n\`\`\`\n${extractedText.slice(0, 15000)}\n\`\`\``
            }
          ];
          modelToUse = 'meta/llama-3.1-8b-instruct'; // Use text model for PDFs
        }
      } catch (e: any) {
        console.error("PDF Parse Error details:", e);
        throw new Error(`Failed to extract text from PDF (${e.message || 'unknown'}). Ensure it is not a scanned image.`);
      }
    } else if (fileType === 'excel' && file.type !== 'text/csv') {
      try {
        const workbook = XLSX.read(buffer, { type: 'buffer' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const extractedText = XLSX.utils.sheet_to_csv(sheet);
        messages = [
          {
            role: "user",
            content: `${PROMPT}\n\nHere is the extracted text from the Excel document:\n\`\`\`\n${extractedText.slice(0, 15000)}\n\`\`\``
          }
        ];
        modelToUse = 'meta/llama-3.1-8b-instruct'; // Use text model for Excel
      } catch (e) {
        throw new Error("Failed to extract text from Excel file.");
      }
    } else if (fileType === 'image') {
      const mime = file.type;
      messages = [
        {
          role: "user",
          content: [
            { type: "text", text: PROMPT },
            {
              type: "image_url",
              image_url: {
                url: `data:${mime};base64,${base64}`
              }
            }
          ]
        }
      ];
    } else if (fileType === 'excel' && file.type === 'text/csv') {
      // CSV: send as text
      const text = Buffer.from(buffer).toString('utf-8');
      messages = [
        {
          role: "user",
          content: `${PROMPT}\n\nHere is the CSV file content:\n\`\`\`\n${text.slice(0, 15000)}\n\`\`\``
        }
      ];
      modelToUse = 'meta/llama-3.1-8b-instruct';
    } else {
      messages = [
        {
          role: "user",
          content: `${PROMPT}\n\nNote: The user uploaded an unsupported file named "${file.name}" (${(file.size / 1024).toFixed(1)} KB). Return empty arrays for data fields.`
        }
      ];
      modelToUse = 'meta/llama-3.1-8b-instruct';
    }

    const response = await ai.chat.completions.create({
      model: modelToUse,
      messages,
      max_tokens: 2048,
    });

    const text  = response.choices[0].message.content ?? '';
    const clean = text.replace(/^```(?:json)?\s*/i, '').replace(/\s*```\s*$/i, '').trim();

    let parsed: any;
    try {
      parsed = JSON.parse(clean);
    } catch {
      parsed = {
        dataType: 'unknown',
        summary: 'Could not parse AI response.',
        rawText: text,
        khata: [],
        stock: [],
        sales: [],
      };
    }

    return NextResponse.json({ ...parsed, fileType });
  } catch (err) {
    console.error('Import API error:', err);
    const errorMessage = err instanceof Error ? err.message : 'Processing failed';
    
    // Return graceful fallback instead of 500 so UI shows the error in summary
    return NextResponse.json({
      dataType: 'unknown',
      summary: `AI Processing Error: ${errorMessage}`,
      rawText: '',
      khata: [],
      stock: [],
      sales: [],
      fileType: 'other',
    });
  }
}
