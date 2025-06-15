import { NextResponse } from "next/server";
import { incView } from "@/lib/db";

export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  const { id } = await context.params;
  await incView(Number(id));
  return NextResponse.json({ ok: true });
}
