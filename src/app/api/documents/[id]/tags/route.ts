import { NextResponse } from "next/server";
import { setTags } from "@/lib/db";

export async function PUT(
  request: Request,
  { params }: { params: { id: string } }
) {
  const { tags } = await request.json();

  if (!Array.isArray(tags)) {
    return NextResponse.json(
      { error: "tags must be array" },
      { status: 400 }
    );
  }

  // Build / tear down the named graph relationships
  await setTags(Number(params.id), tags);
  return NextResponse.json({ ok: true });
}
