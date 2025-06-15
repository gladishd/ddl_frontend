import { NextResponse } from "next/server";
import { incLike } from "@/lib/db";

export async function POST(
  _request: Request,
  { params }: { params: { id: string } }
) {
  // Atomic sub-transaction: increment the like counter
  await incLike(Number(params.id));
  return NextResponse.json({ ok: true });
}
