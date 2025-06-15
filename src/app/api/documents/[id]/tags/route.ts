import { NextRequest, NextResponse } from "next/server";
import { setTags } from "@/lib/db";

export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const { tags } = await req.json();
  if (!Array.isArray(tags))
    return NextResponse.json({ error: "tags must be array" }, { status: 400 });

  // This endpoint builds and tears down 'named' graph relationships.
  await setTags(Number(params.id), tags);
  return NextResponse.json({ ok: true });
}