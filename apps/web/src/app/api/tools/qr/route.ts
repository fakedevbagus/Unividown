import { NextRequest, NextResponse } from 'next/server';
import QRCode from 'qrcode';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const data = searchParams.get('data');
  const size = parseInt(searchParams.get('size') || '300', 10);
  const dark = searchParams.get('dark') || '#000000';
  const light = searchParams.get('light') || '#ffffff';

  if (!data || !data.trim()) {
    return NextResponse.json({ error: 'Parameter "data" is required' }, { status: 400 });
  }

  try {
    const qrDataUrl = await QRCode.toDataURL(data.trim(), {
      width: Math.min(Math.max(size, 100), 1024),
      margin: 2,
      color: {
        dark,
        light,
      },
    });

    return NextResponse.json({ qr: qrDataUrl });
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Failed to generate QR';
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
