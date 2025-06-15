import { NextResponse } from "next/server";
import { setTags } from "@/lib/db";

export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  const { id } = await context.params;
  const { tags } = await request.json();

  if (!Array.isArray(tags)) {
    return NextResponse.json({ error: "tags must be array" }, { status: 400 });
  }

  await setTags(Number(id), tags);
  return NextResponse.json({ ok: true });
}
