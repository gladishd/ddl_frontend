import { NextRequest, NextResponse } from "next/server";
import { incView } from "@/lib/db";

export async function POST(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  // This endpoint records a Local Observer View event.
  await incView(Number(params.id));
  return NextResponse.json({ ok: true });
}