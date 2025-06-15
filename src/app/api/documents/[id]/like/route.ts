import { NextRequest, NextResponse } from "next/server";
import { incLike } from "@/lib/db";

export async function POST(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  // This endpoint executes an atomic subtransaction to increment the like count.
  await incLike(Number(params.id));
  return NextResponse.json({ ok: true });
}