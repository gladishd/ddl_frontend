import { NextResponse } from "next/server";
import { incLike } from "@/lib/db";

export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> }   // 👈 updated type
) {
  const { id } = await context.params;           // 👈 await the promise
  await incLike(Number(id));
  return NextResponse.json({ ok: true });
}
