import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const length = Math.min(Math.max(parseInt(searchParams.get('length') || '16', 10), 4), 128);
  const includeNumbers = searchParams.get('numbers') !== 'false';
  const includeSymbols = searchParams.get('symbols') !== 'false';
  const includeUppercase = searchParams.get('uppercase') !== 'false';

  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const numbers = '0123456789';
  const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?';

  let charset = lowercase;
  if (includeUppercase) charset += uppercase;
  if (includeNumbers) charset += numbers;
  if (includeSymbols) charset += symbols;

  if (charset.length === 0) {
    charset = lowercase;
  }

  // Generate cryptographically secure random characters
  const randomBytes = crypto.randomBytes(length);
  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset[randomBytes[i] % charset.length];
  }

  return NextResponse.json({ password, length });
}
