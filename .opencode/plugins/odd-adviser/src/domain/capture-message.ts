// Domain capture of an admitted chat message: the trimmed text and only the inline base64
// images the parts carry. A path, a remote URL or a non-base64 data URL is ignored, so no
// project file is created or read to evaluate an attached image (S2). This module performs
// no IO.

export type AdmittedPart = {
  readonly text?: string;
  readonly url?: string;
};

export type CapturedImage = {
  readonly mimeType: string;
  readonly base64: string;
};

export type CapturedMessage = {
  readonly text: string;
  readonly images: ReadonlyArray<CapturedImage>;
};

const INLINE_BASE64_DATA_URL = /^data:([^;,]+);base64,([A-Za-z0-9+/=]+)$/;

export function captureMessage(parts: ReadonlyArray<AdmittedPart>): CapturedMessage {
  const text = parts
    .map((part) => (part.text === undefined ? '' : part.text.trim()))
    .filter((part) => part.length > 0)
    .join('\n');

  const images: CapturedImage[] = [];
  for (const part of parts) {
    const match = part.url === undefined ? null : INLINE_BASE64_DATA_URL.exec(part.url);
    if (match === null) continue;
    const [, mimeType, base64] = match;
    if (mimeType === undefined || base64 === undefined) continue;
    images.push({ mimeType, base64 });
  }

  return { text, images };
}
