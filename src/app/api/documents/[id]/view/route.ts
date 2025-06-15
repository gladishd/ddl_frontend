import { NextResponse } from "next/server";
import { incView } from "@/lib/db";

export async function POST(
  _request: Request,
  { params }: { params: { id: string } }
) {
  // Record a Local-Observer view event
  await incView(Number(params.id));
  return NextResponse.json({ ok: true });
}
